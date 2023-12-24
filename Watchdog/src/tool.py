import subprocess,time

from log import LOG

def get_command_output(cmd,discard_lines = [0]):
    ret = list()
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)

    std_out, std_err = proc.communicate()
    i = 0
    if proc.returncode == 0:
        for line in std_out.splitlines():
            if i not in discard_lines:
                ret.append(line)
            i+=1
    else:
        raise Exception(std_err) 
    return ret

def set_containers_gpu_id(cnts,gpus):

    LOG.info("set_containers_gpu_id")

    for i in range(len(cnts.containers)):
        if cnts.containers[i].state != "running":
            cnts.containers[i].force_start()
            time.sleep(10)

        q = get_command_output('docker exec -it '+cnts.containers[i].id+' nvidia-smi --query-gpu=uuid --format=csv',[0])
        if len(q) != 1: raise Exception("Invalid gpu count in container : "+str(cnts.containers[i].name)+" : "+str(len(q)))

        for j in range(len(gpus.gpus)):
            if gpus.gpus[j].uuid == q[0]:
                cnts.containers[i].gpu_id = j
                break

class Singleton:
    __instance = None

    def __new__(cls,*args, **kwargs):
        if cls.__instance is None :
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

class Context(Singleton): pass