#!/usr/bin/python3
# docker run -it --rm --name my-running-script -v "$PWD":/usr/src/myapp -w /usr/src/myapp python:3.7-alpine python script_to_run.py
# docker run -it --rm --name init -v ./src:/usr/src/myapp -w /usr/src/myapp python:3.7-alpine python init.py

import sys,os,json,socket,shutil
from urllib.request import urlopen
sys.path.append("./Watchdog/src/")

from tool import get_command_output

def copy_file_with_process(origin,target, replace = {}, add = list(), uncomment = list()):
    with open(origin, 'r') as file : filedata = file.read()
    for key,value in replace.items(): filedata = filedata.replace(str(key), str(value)) 
    for line in add: filedata = filedata + line + "\n"
    for line in uncomment: filedata = filedata.replace("#"+line, line)
    with open(target, 'w') as file: file.write(filedata)

if __name__ == '__main__':

    TEMPLATE_DIR = "./env/generate.templates/"
    CLIENT_IMAGE_VERSION = "beta.0"

    print("This script will scan your system and try to generate minimalist .env files and docker-compose.yml file\n")    

    gpus_info = list()

    r = get_command_output("nvidia-smi --query-gpu=name,compute_cap --format=csv")
    print("Found following Nvidia gpus : ")
    for i in range(len(r)):
        name,cc = r[i].split(", ")
        m = get_command_output("nvidia-smi -i "+str(i)+" -q -d SUPPORTED_CLOCKS | grep Memory | sed s'/.*: //'",[])
        p = get_command_output("nvidia-smi -i "+str(i)+" -q -d POWER | grep 'Power Limit' | head -5 | tail -2 | sed s'/.*: //'",[])

        mem_list = list()
        for j in range(len(m)):
            mem_list.append(int(m[j].split(" ")[0]))


        for j in reversed(range(len(mem_list))):
            if 100*mem_list[j]/max(mem_list) > 40:
                mem = mem_list[j]
                break

        power = int(p[0].split(".")[0])

        print("{:02d}".format(i)+" : "+name+" with compute capability "+cc+", power saving selected memory clock is "+str(mem)+" and selected power limit is "+str(power))
        gpus_info.append({"name":name, "cc":cc.replace(".",""), "mem":mem, "pl":power})

    print("\nChecking if files already exists : ")
    stop = False
    try:
        if os.path.exists("./.env"): raise Exception(".env file already exists, please remove it first")
        if os.path.exists("./.env.watchdog"): raise Exception(".env.watchdog file already exists, please remove it first")
        for i in range(len(gpus_info)):
            env_name = ".env.gpu."+"{:02d}".format(i)
            if os.path.exists("./.env.gpu."): raise Exception(".env.watchdog file already exists, please remove it first")
        if os.path.exists("./docker-compose.yml"): raise Exception("docker-compose.yml file already exists, please remove it first")
    except Exception as e:
        print(e)
        stop = True

    if stop:
        print("\nExiting : please save/remove your existing .env files")
        exit(-1)
    else: print("OK")

    report = list()

    db_gpu_settings = json.loads(urlopen('http://puzzle.hyenasoft.com:6604/req/gpu-settings-list.php').read())

    print("\nGenerating Main     -> .env")
    copy_file_with_process(TEMPLATE_DIR+".env","./.env")

    watchdog_add = list()
    docker_compose_replace = dict()
    with open(TEMPLATE_DIR+"docker-compose.gpu.yml", 'r') as file : gpu_section_data = file.read()
    gpu_section = ""

    for i in range(len(gpus_info)):
        env_name = ".env.gpu."+"{:02d}".format(i)
        print("Generating gpu "+"{:02d}".format(i)+"   -> "+env_name)
        gpu_replace = dict()
        gpu_uncomment = list()
        gpu_replace["___DELAY___"] = str(10*i)

        found_in_db = False
        for item in db_gpu_settings:
            if item["model"] == gpus_info[i]["name"]+'/':
                found_in_db = True
                break

        if not found_in_db:
            report.append(env_name+" : GPU model "+gpus_info[i]["name"]+" not found in DB")
            report.append(env_name+" : Using default values for ___BIT_OVERRIDE___, ___BLOCKS_OVERRIDE___, ___THREADS_OVERRIDE___, ___POINTS_OVERRIDE___")
            report.append(".env.watchdog : Not defining GPU_MEM_CLOCK_{:02d} and GPU_POWER_LIMIT_{:02d}".format(i,i))
            gpu_replace["___BIT_OVERRIDE___"] = str(40)
            gpu_uncomment.append("BIT_OVERRIDE")
            gpu_replace["___BLOCKS_OVERRIDE___"] = str(32)
            gpu_uncomment.append("BLOCKS_OVERRIDE")
            gpu_replace["___THREADS_OVERRIDE___"] = str(256)
            gpu_uncomment.append("THREADS_OVERRIDE")
            gpu_replace["___POINTS_OVERRIDE___"] = str(256)
            gpu_uncomment.append("POINTS_OVERRIDE")
            watchdog_add.append("")
            watchdog_add.append("#GPU_MEM_CLOCK_"+"{:02d}".format(i)+"=___GPU_MEM_CLOCK___")
            watchdog_add.append("#GPU_POWER_LIMIT_"+"{:02d}".format(i)+"=___GPU_POWER_LIMIT___")
        else:
            gpu_replace["___GPU_MODEL___"] = str(gpus_info[i]["name"])
            gpu_replace["___BIT_OVERRIDE___"] = str(item["min_block_size"]+4)
            gpu_replace["___BLOCKS_OVERRIDE___"] = str(item["blocks"])
            gpu_replace["___THREADS_OVERRIDE___"] = str(item["threads"])
            gpu_replace["___POINTS_OVERRIDE___"] = str(item["points"])
            watchdog_add.append("")
            watchdog_add.append("GPU_MEM_CLOCK_"+"{:02d}".format(i)+"="+str(item["power_save_mem"]))
            watchdog_add.append("GPU_POWER_LIMIT_"+"{:02d}".format(i)+"="+str(item["power_save_pl"]))

        copy_file_with_process(TEMPLATE_DIR+".env.gpu.xx","./"+env_name,gpu_replace,list(),gpu_uncomment)
        gpu_section += gpu_section_data
        gpu_section = gpu_section.replace("___TAG___", "cc"+str(gpus_info[i]["cc"])+"_"+CLIENT_IMAGE_VERSION) 
        gpu_section = gpu_section.replace("___GPU_ID2___", "{:02d}".format(i))
        gpu_section = gpu_section.replace("___GPU_ID___", str(i))

    print("Generating Watchdog -> .env.watchdog")
    watchdog_replace = dict()
    watchdog_replace["___GPU_COUNT___"] = str(len(gpus_info))
    watchdog_replace["___HOSTNAME___"] = str(socket.gethostname().title())
    copy_file_with_process(TEMPLATE_DIR+".env.watchdog","./.env.watchdog",watchdog_replace,watchdog_add)

    print("Generating docker-compose.yml")
    docker_compose_replace["#___GPUS_SECTION___"] = str(gpu_section)
    copy_file_with_process(TEMPLATE_DIR+"docker-compose.yml","docker-compose.yml",docker_compose_replace)

    if len(report) > 0: print("\nFollowing points should be checked : \n\n"+"\n".join(report))
