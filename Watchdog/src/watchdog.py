#!/usr/bin/python3
import time,os

from log import LOG
from tool import Context,get_command_output,hard_reset
from gpu import GpuFactory
from container import ContainerFactory
from webserver import WebserverFactory

if __name__ == '__main__':
    LOG.start()
    LOG.info("Starting ...")
    time.sleep(30)   # let the stack start up when the watchdog starts

    #os.environ["WORKER_GPU_COUNT"] = "6"
    #os.environ["GPU_MEM_CLOCK_00"] = "1200"
    #os.environ["GPU_MEM_CLOCK_01"] = "1300"  
    #os.environ["GPU_POWER_LIMIT_00"] = "100"

    # set overclocking parameters
    gpu_count = os.getenv("WORKER_GPU_COUNT")
    if gpu_count is None: raise Exception("env WORKER_GPU_COUNT is not set")
    gpu_count = int(gpu_count)
    os.system("nvidia-smi -pm 1")
    #get_command_output("nvidia-smi -pm 1")

    for gpu in range(gpu_count):
        mem_clock = os.getenv("GPU_MEM_CLOCK_"+"{:02d}".format(gpu))
        power_limit = os.getenv("GPU_POWER_LIMIT_"+"{:02d}".format(gpu))    
        if mem_clock is not None:
            os.system("nvidia-smi -i "+str(gpu)+" -lmc="+str(mem_clock))
            #get_command_output("nvidia-smi -i "+str(gpu)+" -lmc="+str(mem_clock))
        if power_limit is not None:
            os.system("nvidia-smi -i "+str(gpu)+" -pl "+str(power_limit))
            #get_command_output("nvidia-smi -i "+str(gpu)+" -pl "+str(power_limit))

    try:

        LOG.info("GPU count declared : "+str(gpu_count))

        Context.host_name = os.getenv("HOST_NAME",os.uname()[1])

        Context.gpu_factory = GpuFactory(gpu_count)
        Context.container_factory = ContainerFactory()

        Context.container_factory.refresh_allcontainers() # init containers list
        Context.gpu_factory.start_refresh_thread(10)
        Context.container_factory.start_refresh_thread(30)

        Context.webserver_factory = WebserverFactory()
        Context.webserver_factory.start()

        previous_gpu_count = gpu_count
        while True:

            try:
                q = get_command_output('nvidia-smi'+GpuFactory.STATE_QUERY_PARAMS)
                if len(q) != Context.gpu_factory.count and previous_gpu_count != gpu_count:
                    raise Exception("Invalid gpu count : "+str(gpu_count)+" != "+str(len(q)))
            except Exception as e:
                LOG.fatal("Exception : "+str(e)+" gpu may be unresponsive, applying hard reset")
                hard_reset()
                exit(-1)

            previous_gpu_count = len(q)
            time.sleep(60)

    except Exception as e:
        LOG.error(e)
        exit(-1)


# Hung system :
# https://linuxhandbook.com/frozen-linux-system/
# https://www.kernel.org/doc/html/latest/admin-guide/sysrq.html
# https://www.shellhacks.com/remote-hard-reset-linux-server-reboot-not-work/
# echo s | sudo tee /proc/sysrq-trigger
# echo b | sudo tee /proc/sysrq-trigger
