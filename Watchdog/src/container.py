import json,time,threading
from tool import get_command_output
from log import LOG

class Container():
    def __init__(self,js,pool,worker):
        self.name = js['Names']
        self.id = js['ID']
        self.state = js['State']
        self.status = js['Status']
        self.gpu_id = None
        self.restart = 1
        self.last_restart = time.time()
        self.pool = pool
        self.worker = worker

    def to_html(self,idx):
        warnings,is_warnings = self.get_warnings()
        ret = "<tr"+(" class='highlight'" if is_warnings else "")+"><td>"+str(idx)+"</td><td>"+str(self.gpu_id)+"</td><td>"+str(self.name)+"</td><td>"+str(self.id)+"</td><td>"+str(self.status)+"</td><td>"+ str(self.state)+"</td><td>"+str(self.restart)+"</td><td>"+str(self.pool)+"</td><td>"+str(self.worker)+"</td><td>"+str(warnings)+"</td><tr>"
        return ret        

    def update(self,js,pool,worker):
        self.state = js['State']
        self.status = js['Status']
        self.pool = pool
        self.worker = worker

    def get_warnings(self):
        ret = ""
        failed = False
        if self.state != "running":
            ret += "STATE "
            failed = True
        if self.pool is None:
            ret += "POOL "
        if ret == "": ret = "OK"
        return ret, failed

    def force_start(self):
        now = time.time()
        if now - self.last_restart < 600:     # 10 minutes between 2 restarts is believe to be restarts in a row
            self.restart+=1

            if self.restart > 5:   # to many restarts in a row : need to reset GPU
                LOG.error("Too many restarts for container "+str(self.name))
                #TODO

        else:
            self.restart=1
        self.last_restart = now

        # TODO add restart in a centralized queue to avoid concurrent restarts of containers

        o = get_command_output('docker start '+str(self.name),[])
        LOG.warning("Restarting container "+str(self.name)+" : "+str(o))

class ContainerFactory():

    def __init__(self,count):
        self.count = count
        self.containers = list()
        self.refresh_thread = None

        self.restart_containers = set()

        r = get_command_output('docker container ls -a --filter name=bitcrack-client --format json',[])
        if len(r) != self.count: raise Exception("Invalid container count in snapshot : "+str(self.count)+" != "+str(len(r)))

        sdr = sorted([json.loads(x) for x in r], key=lambda d: d['Names'])
        for i in range(0,self.count):

            pool = None
            worker = None
            try:
                for item in get_command_output("docker exec -it "+sdr[i]['Names']+" bash -c 'cat /proc/`ps -A | grep BitCrack | awk \"{ print \\\$1 }\"`/environ | tr \"\\000\" \"\\n\"'",[]):
                    if item.startswith("POOL_NAME="): pool = item.split("=")[1]
                    if item.startswith("WORKER_NAME="): worker = item.split("=")[1]
            except Exception as e:
                LOG.error("Exception : "+str(e))
 
            self.containers.append(Container(sdr[i],pool,worker))

    def __del__(self):
        if self.refresh_thread != None: self.refresh_thread.join()

    def to_html(self):
        ret = "<table id='containers' class='bordered'><tr class='header'><th>Container</th><th>Gpu</th><th>Name</th><th>Id</th><th>Status</th><th>State</th><th>Restart</th><th>Pool</th><th>Worker</th><th></th></tr>"
        for i in range(self.count): ret += self.containers[i].to_html(i)
        return ret+ "</table>"
    
    def logs_to_html(self):
        ret = "<table id='logs' class='bordered'><tr class='header'><th>Container</th><th>Date</th><th>Block duration</th><th>Scan speed</th></tr>"
        logs = list()

        for i in range(self.count):
            for item in get_command_output("docker logs "+str(self.containers[i].name)+" | grep 'Scan done' | tail -5",[]):
                logs.append((i,item.split("INFO")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[1]))

        slogs = sorted(logs, key=lambda d: d[1], reverse=True)

        for j in slogs:
            ret += "<tr><td>"+str(j[0])+"</td><td>"+str(j[1])+"</td><td>"+str(j[2])+"</td><td>"+str(j[3])+"</td></tr>"
            
        return ret+ "</table>"

    def get_container_from_name(self,name):
        for c in self.containers:
            if c.name == name: return c

    def refresh(self):
        threading.current_thread().name = "ContainersRefresh"

        while True:
            time.sleep(60)
            LOG.info("Refreshing")
            self.refresh_allcontainers()

            for item in self.containers:
                if item.get_warnings()[1] == True:
                    item.force_start()      # TODO add item in the queue
                    time.sleep(5)           # for the moment take 5 sec delay between restarts (it seems if many workers are started at same time nvidia drivers may hang)

            #TODO : restart one container at a time

    def refresh_allcontainers(self):
        r = get_command_output('docker container ls -a --filter name=bitcrack-client --format json',[])
        sdr = sorted([json.loads(x) for x in r], key=lambda d: d['Names'])
        for i in range(len(sdr)):

            pool = None
            worker = None
            try:
                for item in get_command_output("docker exec -it "+sdr[i]['Names']+" bash -c 'cat /proc/`ps -A | grep BitCrack | awk \"{ print \\\$1 }\"`/environ | tr \"\\000\" \"\\n\"'",[]):
                    if item.startswith("POOL_NAME="): pool = item.split("=")[1]
                    if item.startswith("WORKER_NAME="): worker = item.split("=")[1]
            except Exception as e:
                LOG.error("Exception : "+str(e))
 
            self.get_container_from_name(sdr[i]['Names']).update(sdr[i],pool,worker)

    def start_refresh_thread(self,interval):
        self.refresh_thread = threading.Thread(target = self.refresh)
        self.refresh_thread.start()

