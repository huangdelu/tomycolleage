#!/usr/bin/python
#_*_coding:utf-8_*_

import psutil
import time
import docker
import traceback
def sub_cpu_percent(item,cpu_percent):
    if not item.children():
       cpu_percent = item.cpu_percent()
       return float(cpu_percent)
    for child_item in item.children():
        #print(child_item.name)
        cpu_percent += sub_cpu_percent(child_item, cpu_percent)
        #print(return_val[0],return_val[1])
    #print(sum_cpu)

    return cpu_percent

def sub_mem_total(item,sum_memory):
    if not item.children():
       sum_memory = item.memory_info()[0]
       return float(sum_memory)
    for child_item in item.children():
        #print(child_item.name)
        sum_memory += sub_mem_total(child_item, sum_memory)
    return sum_memory


def get_cpu_mem_percent():
    for pid in psutil.pids():
        if(psutil.Process(pid).name()=="docker-containerd-current"):
            containerd = psutil.Process(pid)
            break
    all_list = []

    for shim in containerd.children():
        each_item = []
        each_item.append(shim.cmdline()[1][:10])

        shim_cpu= sub_cpu_percent(shim,0)
        shim_memory = sub_mem_total(shim,0)

        each_item.append(shim_cpu)
        each_item.append(shim_memory)
        all_list.append(each_item)

    container_id_list = set([x[0] for x in all_list])
    save_data = list(map(lambda x: [x, 0, 0], container_id_list))
    for each_shim in all_list:
        for i in range(len(save_data)):
            if each_shim[0] == save_data[i][0]:
                save_data[i][1] += each_shim[1]
                save_data[i][2] += each_shim[2]
    return save_data

def get_running_data():
    try:
        client = docker.from_env()
    except:
        print("创建client失败")
        return False
    try:

        all_result = []
        each_result = []
        for container in client.containers.list():
            result = container.stats(decode=True).next()
            process = container.top()["Processes"]
            mem_limit = round(float(result["memory_stats"]["limit"]) / 1024 / 1024, 2)
            each_result = [container.short_id, mem_limit,process]
            all_result.append(each_result)
        return all_result
    except Exception as e:
        print("error occur:%s"%e)
    finally:
        client.close()


