import http.server,threading,os
import socketserver
import ssl
#import base64
from tool import Context
from log import LOG

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
            self.send_header('Access-Control-Allow-Origin', '*')
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

        if self.url_lookup("/json/gpus?",Context.gpu_factory.to_json): return
        if self.url_lookup("/json/containers?",Context.container_factory.to_json): return
        if self.url_lookup("/json/logs?",Context.container_factory.logs_to_json): return

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

    if not os.path.exists('/app/ssl'): os.mkdir('/app/ssl')
    if not os.path.exists('/app/ssl/cert.pem') or not os.path.exists('/app/ssl/key.pem'):
        if os.path.exists('/app/ssl/cert.pem'): os.remove('/app/ssl/cert.pem')
        if os.path.exists('/app/ssl/key.pem'): os.remove('/app/ssl/key.pem')
        LOG.info("Generating SSL Certificate")
        try:
            OpenSslCommand = 'openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes -out /app/ssl/cert.pem -keyout /app/ssl/key.pem -subj "/C=IN/ST=Maharashtra/L=Satara/O=Self signed certifcate/OU='+os.uname()[1]+'/CN=www.hyenasoft.com"'
            os.system(OpenSslCommand)
            LOG.info('<<<<Certificate Generated>>>>>>')
        except:
            LOG.error('error while generating certificate')
    else:
        LOG.info("SSL Certificate already exists")

    Handler = WebserverRequestHandler
    PORT = 443

    Context.webserver_factory.webserver = http.server.HTTPServer(("", PORT), Handler)
    Context.webserver_factory.webserver.socket = ssl.wrap_socket(Context.webserver_factory.webserver.socket,
                                server_side=True,
                                certfile = "/app/ssl/cert.pem",
                                keyfile = "/app/ssl/key.pem",
                                ssl_version=ssl.PROTOCOL_TLSv1_2)

    LOG.info("serving at port "+str(PORT))
    Context.webserver_factory.webserver.serve_forever() 

class WebserverFactory():

    def __init__(self):
        self.webserver_thread = None
        self.webserver = None

    def __del__(self):
        if self.webserver_thread != None: self.webserver_thread.join()        

    def start(self):
        LOG.info("Starting Webserver")
        self.webserver_thread = threading.Thread(target = WebserverThread)
        self.webserver_thread.start()

    def stop(self):
        LOG.info("Stopping Webserver")
        if self.webserver is not None: self.webserver.shutdown()
        if self.webserver_thread is not None: self.webserver_thread.join()
