#!/usr/bin/python
#_*_coding:utf-8_*_

import tornado.ioloop
import tornado.web
import os
import DockerPs
import logging
import ContainerStat
import json
import sqlite3
import time

class indexHandler(tornado.web.RequestHandler):
    def get(self):
        kernel,dockerversion,cpu_num,mem_total = DockerPs.IndexMessage()
        mem_total = round(mem_total,2)

        containers,images = DockerPs.DockerInfo()
        container_num = len(containers)
        image_num = len(images)
        self.render("index.html",kernel=kernel,docker=dockerversion,cpu=cpu_num,mem=mem_total,container_num=container_num,\
                    image_num=image_num)

class containerHandler(tornado.web.RequestHandler):
    def get(self):
        container_list = DockerPs.DockerInfo()[0]

        # 将信息处理成列表
        container_list = list(map(lambda x: x.split("\t"), container_list))
        self.render("containers.html",Containers=container_list)
class statsHandler(tornado.web.RequestHandler):
    def get(self):
        cpu_mem_percent = ContainerStat.get_cpu_mem_percent()
        running_data = ContainerStat.get_running_data()
        for each_cpu_percent in cpu_mem_percent:
            for each_data in running_data:
                if each_cpu_percent[0] == each_data[0]:
                    each_cpu_percent += each_data[1:]
        self.render("stats.html",result=cpu_mem_percent)
class imageHandler(tornado.web.RequestHandler):
    def get(self):
        image_list = DockerPs.DockerInfo()[1]

        # 将信息处理成列表
        image_list = list(map(lambda x: x.split("\t"), image_list))
        self.render("image.html",Images=image_list)
class getstatHandler(tornado.web.RequestHandler):
    def get(self):
        cpu_mem_percent = ContainerStat.get_cpu_mem_percent()
        running_data = ContainerStat.get_running_data()
        for each_cpu_percent in cpu_mem_percent:
            for each_data in running_data:
                if each_cpu_percent[0] == each_data[0]:
                    each_cpu_percent += each_data[1:]
        #print(cpu_mem_percent)
        result = list(map(lambda x:{'id':x[0],'cpu_p':x[1],'mem_p':round(float(x[2]/1024/1024/x[3])*100,2),\
                                    'mem_u':round(float(x[2])/1024/1024,2),'mem_t':x[3],'process':x[4]},cpu_mem_percent))
        jsondata = json.dumps(result)
        self.write(jsondata)
        #self.write("Hello World\n")

class DetectHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("404.html")
    def post(self):
        #获取传回来的数据  包括容器ID和容器ID
        ID = self.get_argument("containerID")
        print(ID)
        if ID.split(":")[0] == "C":
            if DockerPs.Container_tar(ID.split(":")[1]):
                logger.info("容器压缩文件上传成功!\n")
            else:
                logger.error("容器压缩文件上传失败!\n")

        if ID.split(":")[0] == "I":
            if DockerPs.Image_tar(ID.split(":")[1]):
                logger.info("镜像压缩文件上传成功!\n")
            else:
                logger.error("镜像压缩文件上传失败!\n")

class ViewHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("404.html")
    def post(self):
        try:
            ID = self.get_argument("containerID")
        except Exception as e:
            self.render("noid.html")
        ID = "5df70c6adf8b"
        resultdb = os.path.join(os.path.abspath("detect_result"),"%s.db"%ID)
        if not os.path.exists(resultdb):
            self.render("notresult.html")
        else:
            try:
                try:
                    conn = sqlite3.connect(resultdb)
                    cur = conn.cursor()
                except Exception as e:
                    logger.error("connect result database %s.db error:%s"%(ID,e))
                    self.write("open database fail!!!")
                #获取info数据
                try:
                    infosql = "select * from info"
                    cur.execute(infosql)
                    info = cur.fetchall()
                except Exception as e:
                    logger.error("search info error:%s"%(e))
                #获取cve数据
                try:
                    cveinfo = "select * from CVE"
                    cur.execute(cveinfo)
                    cve = cur.fetchall()
                    cveinfo = list(map(lambda x:list(x),cve))
                    for index in range(len(cveinfo)):
                        cveinfo[index][11] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(cve[index][11]))
                        cveinfo[index][12] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cve[index][12]))
                except Exception as e:
                    logger.error("search cve data error:%s"%e)
                #获取恶意文件检测结果
                try:
                    malwareinfo = "select * from malware"
                    cur.execute(malwareinfo)
                    malware = cur.fetchall()
                except Exception as e:
                    logger.error("search malware data error:%s"%e)
                #获取程序列表
                try:
                    programinfo = "select * from program"
                    cur.execute(programinfo)
                    program = cur.fetchall()
                except Exception as e:
                    logger.error("search program data error:%s"%e)
                self.render("detect.html",info = info[0],cve_list = cveinfo,program_list = program,malware_list = malware)
            except Exception as e:
                logger.error("occur error :%s"%(e))
                self.render("notresult.html")
class ResultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("404.html")
    def post(self):
        remote_ip = self.request.remote_ip
        meta = self.request.files["file"][0]
        filename = meta["filename"]
        # 结果保存数据库
        savepath = os.path.join(os.path.abspath("detect_result"), os.path.split(filename)[1])
        filedata = meta["body"]
        try:
            if os.path.exists(savepath):
                logger.warning("数据库结果已存在  开始覆写")
            with io.open(savepath, "wb") as fp:
                fp.write(filedata)
            logger.info("save database %s success" %(os.path.split(filename)[1]))
        except Exception as e:
            logger.error("save database %s Failed as %s"%(os.path.split(filename)[1],e))



def make_app():
    #生成tornado对象
    #设置调试模式、静态文件路径、网页模板路径
    settings={'debug':True,
              "xsrf_cookies": False,
              'static_path':os.path.join(os.path.dirname(__file__),"static"),
              'template_path':os.path.join(os.path.dirname(__file__),"templates"),
              }

    #生成tornado对象
    return tornado.web.Application([
        (r"/", indexHandler),
        (r"/containers",containerHandler),
        (r"/stats",statsHandler),
        (r"/getstat",getstatHandler),
        (r"/images",imageHandler),
        (r"/detect",DetectHandler),
        (r"/result",ResultHandler),
        (r"/view_detect",ViewHandler)
    ],**settings)

if __name__ == "__main__":
    #返回名字 可供程序直接调用的接口
    logger = logging.getLogger("Client")
    #设置容器级别  设置为debug才显示debug信息
    logger.setLevel(level=logging.INFO)

    #将日志存储在文件中 将日志记录分配至正确的目的地
    handler = logging.FileHandler("log.txt")
    # 设置容器级别  设置为debug才显示debug信息
    handler.setLevel(logging.INFO)
    #日志内容格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    #给logger添加handler
    logger.addHandler(handler)


    #tornado对象
    app = make_app()
    #监听5000端口
    app.listen(5000)
    #启动监听
    tornado.ioloop.IOLoop.current().start()
