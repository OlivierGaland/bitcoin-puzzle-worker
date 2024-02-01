import subprocess,time,os

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
        raise Exception("Error executing : "+str(cmd)+" / "+str(proc.returncode)+" / "+str(std_out)+" / "+str(std_err)) 
    return ret

class Singleton:
    __instance = None

    def __new__(cls,*args, **kwargs):
        if cls.__instance is None :
            cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

class Context(Singleton): pass


def hard_reset():
    LOG.info("Closing all watchdog threads")
    Context.gpu_factory.refresh_thread_to_kill = True
    Context.container_factory.refresh_thread_to_kill = True
    Context.gpu_factory.refresh_thread.join()
    Context.container_factory.refresh_thread.join()
    Context.webserver_factory.stop()
    time.sleep(10)

    LOG.info("Closing all containers")
    for item in Context.container_factory.containers:
        try:
            item.force_stop()
        except Exception as e:
            LOG.error("Exception : "+str(e))
    time.sleep(20)

    LOG.info("Syncing drives")
    os.system("echo s | tee /proc/sysrq-trigger")
    time.sleep(10)
    LOG.info("Reseting")
    os.system("echo b | tee /proc/sysrq-trigger")

