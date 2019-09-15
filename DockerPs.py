#!/usr/bin/python
#_*_coding:utf-8_*_

import os
import docker
import tempfile
import requests
import logging
import psutil
DockerPslogger = logging.getLogger("Client.sub")

def DockerInfo():
    #获取容器列表
    container_list = os.popen('docker ps  --format "{{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.Command}}\t{{.Names}}\t{{.Size}}"').read().split("\n")

    #镜像列表
    image_list = os.popen('docker image ls --format "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"').read().split("\n")
    return container_list[:-1],image_list[:-1]

#获取容器ID并将容器打包成tar文件

def Container_tar(ID):

    try:
        # 建立Docker API 对象
        client = docker.from_env()

        #获取对应容器文件的镜像内容
        container_content = client.containers.get(ID).export()

        #创建临时文件，关闭后删除  不会占用空间
        fp  = tempfile.TemporaryFile()
        #写入镜像文件
        for chunk in container_content:
            fp.write(chunk)
        #回到文件开头，准备传送数据
        fp.seek(0)
    except Exception as e:
        DockerPslogger.error("容器打包成压缩文件失败:%s"%(e))
        return 'False'

    # 传输数据
    try:
        #静态检测模块接收地址
        url = "http://127.0.0.1:8000/file"

        #发送文件
        SendFile = {'file': ("%s.export"%ID,fp)}
        #flag为服务端接收信息  成功返回True
        requests.post(url,files=SendFile)

    except Exception as e:
        DockerPslogger.error("容器压缩文件发送失败:%s"%(e))
        return False

    #关闭文件 临时文件被删除
    fp.close()
    #关闭docker API对象
    container_content.close()
    client.close()

    #成功发送的flag
    return True


# 获取镜像ID并将镜像打包成tar文件

def Image_tar(ID):
    try:
        # 建立Docker API 对象
        client = docker.from_env()

        # 获取对应镜像文件的镜像内容
        container_content = client.images.get(ID).save()

        # 创建临时文件，关闭后删除  不会占用空间
        fp = tempfile.TemporaryFile()
        # 写入镜像文件
        for chunk in container_content:
            fp.write(chunk)
        # 回到文件开头，准备传送数据
        fp.seek(0)
    except Exception as e:
        DockerPslogger.error("镜像打包成压缩文件失败:%s" % (e))
        return False

    # 传输数据
    try:
        # 静态检测模块接收地址
        url = "http://127.0.0.1:8000/file"

        # 发送文件
        SendFile = {'file': ("%s.save" % ID, fp)}
        requests.post(url, files=SendFile)

    except Exception as e:
        DockerPslogger.error("镜像压缩文件发送失败:%s" % (e))
        return False
    # 关闭文件 临时文件被删除
    fp.close()
    # 关闭docker API对象
    container_content.close()
    client.close()
    # 成功发送的flag
    return True
def IndexMessage():
    kernel = dockerversion = cpu_num =mem_total =''
    try:
        client = docker.from_env()
        kernel = client.version()["KernelVersion"]
        dockerversion = client.version()["Version"]
        cpu_num = psutil.cpu_count(logical=False)
        mem_total = float(psutil.virtual_memory().total)/1024/1024

        client.close()
        return kernel,dockerversion,cpu_num,mem_total
    except Exception as e:
        DockerPslogger.error("connect to docker daemon error:%s"%e)
        return '','','',''


