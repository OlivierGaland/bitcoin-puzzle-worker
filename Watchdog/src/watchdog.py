#!/usr/bin/python3
import time,os

from log import LOG
from tool import Context,get_command_output
from gpu import GpuFactory
from container import ContainerFactory
from webserver import WebserverFactory

def hard_reset():
    LOG.info("Closing all watchdog threads")
    Context.gpu_factory.refresh_thread_to_kill = True
    Context.container_factory.refresh_thread_to_kill = True
    Context.gpu_factory.refresh_thread.join()
    Context.container_factory.refresh_thread.join()
    Context.webserver_factory.stop()
    time.sleep(10)

    LOG.info("Closing all containers")
    for item in Context.container_factory.containers: item.force_stop()
    time.sleep(20)

    LOG.info("Syncing drives")
    os.system("echo s | sudo tee /proc/sysrq-trigger")
    time.sleep(10)
    LOG.info("Reseting")
    os.system("echo b | sudo tee /proc/sysrq-trigger")



if __name__ == '__main__':
    LOG.start()
    LOG.info("Starting ...")

    #os.environ["WORKER_GPU_COUNT"] = "6"
    #os.environ["GPU_MEM_CLOCK_00"] = "1200"
    #os.environ["GPU_MEM_CLOCK_01"] = "1300"  
    #os.environ["GPU_POWER_LIMIT_00"] = "100"

    # set overclocking parameters
    gpu_count = os.getenv("WORKER_GPU_COUNT")
    if gpu_count is None: raise Exception("env WORKER_GPU_COUNT is not set")
    gpu_count = int(gpu_count)
    os.system("nvidia-smi -pm 1")
    for gpu in range(gpu_count):
        mem_clock = os.getenv("GPU_MEM_CLOCK_"+"{:02d}".format(gpu))
        power_limit = os.getenv("GPU_POWER_LIMIT_"+"{:02d}".format(gpu))    
        if mem_clock is not None:
            os.system("nvidia-smi -i "+str(gpu)+" -lmc="+str(mem_clock))
        if power_limit is not None:
            os.system("nvidia-smi -i "+str(gpu)+" -pl "+str(power_limit))

    try:

        LOG.info("GPU count declared : "+str(gpu_count))

        Context.gpu_factory = GpuFactory(gpu_count)
        Context.container_factory = ContainerFactory()

        Context.container_factory.refresh_allcontainers() # init containers list
        Context.gpu_factory.start_refresh_thread(10)
        Context.container_factory.start_refresh_thread(30)

        Context.webserver_factory = WebserverFactory()
        Context.webserver_factory.start()

        previous_gpu_count = gpu_count
        while True:

            # Check if no gpu is down
            q = get_command_output('nvidia-smi'+GpuFactory.STATE_QUERY_PARAMS)

            if len(q) != Context.gpu_factory.count and previous_gpu_count != gpu_count:
                LOG.fatal("Invalid gpu count, one may be down, applying hard reset : "+str(gpu_count)+" != "+str(len(q)))
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
