#!/usr/bin/python3
import time,subprocess,os
import threading

import base64

import http.server
import socketserver

from log import LOG
from tool import Context,get_command_output
from gpu import GpuFactory
from container import ContainerFactory

class WebserverRequestHandler(http.server.SimpleHTTPRequestHandler):

    URL_MAPPING = {
        "/" : "watchdog.html",
        "/favicon.ico" : "favicon.ico",
        "/www/style.css" : "style.css",
        "/www/logo.png" : "logo.png",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, directory='/www')

    def log_request(self, code='-', size='-'):
        pass

    def url_lookup(self,url,fct):
        if self.path.startswith(url):
            self.send_response(200)
            self.end_headers()
            ret = fct()
            self.wfile.write(bytes(ret, "utf-8"))
            return True
        return False

    def url_abs_lookup(self,url):
        if self.path == url:
            self.path = WebserverRequestHandler.URL_MAPPING[url]
            return True
        return False

    # def url_pic_lookup(self,url):

    #     if self.path.startswith("/logo?"):
        #     self.send_response(200)
        #     self.send_header("Content-type", "image/jpeg")
        #     self.end_headers()

        #     ret = None
        #     with open('./webserver/logo.png', 'rb') as file_handle:
        #         ret = file_handle.read()

        #     code = '<img src="data:image/jpeg;base64,'+base64.b64encode(ret).decode('utf-8')+'" />'

        #     self.wfile.write(bytes(code, "utf-8"))
        #     return 




    def do_GET(self):
        LOG.info("GET "+str(self.path))

        if self.url_lookup("/gpus?",Context.gpu_factory.to_html): return
        if self.url_lookup("/containers?",Context.container_factory.to_html): return
        if self.url_lookup("/logs?",Context.container_factory.logs_to_html): return

        if self.url_abs_lookup("/www/style.css"): return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.url_abs_lookup("/www/style.css"): return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.url_abs_lookup("/www/logo.png"): return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.url_abs_lookup("/favicon.ico"): return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.url_abs_lookup("/"): return http.server.SimpleHTTPRequestHandler.do_GET(self)

        self.send_response(500)
        self.end_headers()
        return



def WebserverThread():
    threading.current_thread().name = "Webserver"

    Handler = WebserverRequestHandler

    PORT = 80
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        LOG.info("serving at port "+str( PORT))
        httpd.serve_forever() 

    httpd.socket.close()
    httpd.shutdown()       


def hard_reset():
    LOG.info("Closing all watchdog threads")
    Context.gpu_factory.refresh_thread_to_kill = True
    Context.container_factory.refresh_thread_to_kill = True
    Context.gpu_factory.refresh_thread.join()
    Context.container_factory.refresh_thread.join()
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

        webserver_thread = None
        Context.gpu_factory = GpuFactory(gpu_count)
        Context.container_factory = ContainerFactory()
        Context.container_factory.refresh_allcontainers() # init containers list

        Context.gpu_factory.start_refresh_thread(10)
        Context.container_factory.start_refresh_thread(30)

        webserver_thread = threading.Thread(target = WebserverThread)
        webserver_thread.start()


        previous_gpu_count = gpu_count
        while True:

            # Check if no gpu is down
            q = get_command_output('nvidia-smi'+GpuFactory.STATE_QUERY_PARAMS)

            if len(q) != Context.gpu_factory.count and previous_gpu_count != gpu_count:
                LOG.fatal("Invalid gpu count, one may be down, applying hard reset : "+str(self.count)+" != "+str(len(q)))
                hard_reset()
                exit(-1)
            previous_gpu_count = len(q)

            time.sleep(60)

    except Exception as e:
        LOG.error(e)
        if webserver_thread is not None: webserver_thread.join()
        exit(-1)


# Hung system :
# https://linuxhandbook.com/frozen-linux-system/
# https://www.kernel.org/doc/html/latest/admin-guide/sysrq.html
# https://www.shellhacks.com/remote-hard-reset-linux-server-reboot-not-work/
# echo s | sudo tee /proc/sysrq-trigger
# echo b | sudo tee /proc/sysrq-trigger
