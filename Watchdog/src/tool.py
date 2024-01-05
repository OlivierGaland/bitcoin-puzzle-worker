import subprocess,time

from log import LOG

def get_command_output(cmd,discard_lines = [0]):
    ret = list()
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)

    try:
        std_out, std_err = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        raise Exception("Timeout : "+str(cmd))

    i = 0
    if proc.returncode == 0:
        for line in std_out.splitlines():
            if i not in discard_lines:
                ret.append(line)
            i+=1
    else:
        raise Exception(std_err) 
    return ret

class Singleton:
    __instance = None

    def __new__(cls,*args, **kwargs):
        if cls.__instance is None :
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

class Context(Singleton): pass