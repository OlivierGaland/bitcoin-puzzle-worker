#!/usr/bin/python3
import time,subprocess,os
import threading

import base64

import http.server
import socketserver

from log import LOG
from tool import Context,get_command_output,set_containers_gpu_id
from gpu import GpuFactory
from container import ContainerFactory

class WebserverRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, directory='/www')

    def log_request(self, code='-', size='-'):
        pass

    def do_GET(self):

        LOG.info("GET "+str(self.path))

        if self.path.startswith("/gpus?"):
            self.send_response(200)
            self.end_headers()
            ret = Context.gpu_factory.to_html()
            self.wfile.write(bytes(ret, "utf-8"))
            return

        if self.path.startswith("/containers?"):
            self.send_response(200)
            self.end_headers()
            ret = Context.container_factory.to_html()
            self.wfile.write(bytes(ret, "utf-8"))
            return

        if self.path.startswith("/logs?"):
            self.send_response(200)
            self.end_headers()
            ret = Context.container_factory.logs_to_html()
            self.wfile.write(bytes(ret, "utf-8"))
            return

        if self.path.startswith("/pools?"):
            self.send_response(200)
            self.end_headers()
            ret = "TODO"
            #ret = Context.container_factory.logs_to_html()
            self.wfile.write(bytes(ret, "utf-8"))
            return        

        #https://stackoverflow.com/questions/28567733/how-to-encode-image-to-send-over-python-http-server
        # if self.path.startswith("/logo?"):
        #     self.send_response(200)
        #     self.send_header("Content-type", "image/jpeg")
        #     self.end_headers()

        #     ret = None
        #     with open('./webserver/logo.png', 'rb') as file_handle:
        #         ret = file_handle.read()

        #     code = '<img src="data:image/jpeg;base64,'+base64.b64encode(ret).decode('utf-8')+'" />'

        #     self.wfile.write(bytes(code, "utf-8"))
        #     return 


        if self.path.startswith("/www/style.css"):
            self.path = 'style.css'
        elif self.path.startswith("/www/logo.png"):
            self.path = 'logo.png'
        else:
            self.path = 'watchdog.html'   # care of this (could end with infinite nested page if ajax queries name are not added)

        return http.server.SimpleHTTPRequestHandler.do_GET(self)



def WebserverThread():
    threading.current_thread().name = "Webserver"

    Handler = WebserverRequestHandler

    PORT = 80
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        LOG.info("serving at port "+str( PORT))
        httpd.serve_forever() 

    httpd.socket.close()
    httpd.shutdown()       


if __name__ == '__main__':
    LOG.start()
    LOG.info("Starting ...")
    time.sleep(15)  # timer for workers containers to be up

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

        LOG.info("GPU count : "+str(gpu_count))

        webserver_thread = None
        Context.gpu_factory = GpuFactory(gpu_count)
        Context.container_factory = ContainerFactory(gpu_count)

        #exit(-1)

        set_containers_gpu_id(Context.container_factory,Context.gpu_factory)

        Context.gpu_factory.start_refresh_thread(10)
        Context.container_factory.start_refresh_thread(30)

        webserver_thread = threading.Thread(target = WebserverThread)
        webserver_thread.start()


        while True:
            time.sleep(5)

    except Exception as e:
        LOG.error(e)
        if webserver_thread is not None: webserver_thread.join()
        exit(-1)


# Hung system :
# https://linuxhandbook.com/frozen-linux-system/
# https://www.kernel.org/doc/html/latest/admin-guide/sysrq.html

