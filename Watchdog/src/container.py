import json,time,threading,os
from tool import Context,get_command_output
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

    def to_dict(self):
        warnings,is_warnings = self.get_warnings()
        ret = {
            "name" : self.name,
            "id" : self.id,
            "state" : self.state,
            "status" : self.status,
            "gpu_id" : self.gpu_id,
            "restart" : self.restart,
            "pool" : self.pool,
            "worker" : self.worker,
            "warnings" : warnings
        }
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

    def set_gpu_id(self):
        try:
            q = get_command_output('docker exec -it '+self.id+' nvidia-smi --query-gpu=uuid --format=csv',[0])
            if len(q) != 1: raise Exception("Invalid gpu count in container : "+str(self.name)+" : "+str(len(q)))

            gpu_f = Context.gpu_factory
            self.gpu_id = None
            for j in range(len(gpu_f.gpus)):
                if gpu_f.gpus[j].uuid == q[0]:
                    self.gpu_id = j
                    break

        except Exception as e:
            LOG.error("Exception : "+str(e))


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

    def force_stop(self):
        o = get_command_output('docker stop '+str(self.name),[])
        LOG.warning("Stopping container "+str(self.name)+" : "+str(o))

class ContainerFactory():

    def __init__(self):
        self.containers = list()
        self.refresh_thread = None
        self.refresh_thread_to_kill = False

    def __del__(self):
        if self.refresh_thread != None: self.refresh_thread.join()


    def to_json(self):
        ret = dict()
        ret["host"] = Context.host_name
        ret["containers"] = list()
        for c in self.containers: ret["containers"].append(c.to_dict())
        return json.dumps(ret)

    def to_html(self):
        ret = "<table id='containers_tab' class='bordered'><tr class='header'><th>Container</th><th>Gpu</th><th>Name</th><th>Id</th><th>Status</th><th>State</th><th>Restart</th><th>Pool</th><th>Worker</th><th></th></tr>"
        for i in range(len(self.containers)): ret += self.containers[i].to_html(i)
        return ret+ "</table>"
    
    def logs_to_html(self):
        ret = "<table id='logs_tab' class='bordered'><tr class='header'><th>Container</th><th>Date</th><th>Block duration</th><th>Scan speed</th></tr>"
        logs = list()

        nline = 0 if len(self.containers) == 0 else int(36/len(self.containers))

        for i in range(len(self.containers)):
            for item in get_command_output("docker logs "+str(self.containers[i].name)+" | grep 'Scan done' | tail -"+str(nline),[]):
                logs.append((i,item.split("INFO")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[1]))

        slogs = sorted(logs, key=lambda d: d[1], reverse=True)

        for j in slogs:
            ret += "<tr><td>"+str(j[0])+"</td><td>"+str(j[1])+"</td><td>"+str(j[2])+"</td><td>"+str(j[3])+"</td></tr>"
            
        return ret+ "</table>"
    
    def logs_to_json(self):
        ret = dict()
        ret["host"] = Context.host_name
        ret["logs"] = list()
        logs = list()

        nline = 0 if len(self.containers) == 0 else int(36/len(self.containers))

        for i in range(len(self.containers)):
            for item in get_command_output("docker logs "+str(self.containers[i].name)+" | grep 'Scan done' | tail -"+str(nline),[]):
                logs.append((i,item.split("INFO")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[0].split(".")[0],item.split("elapsed time")[1].split(" speed is ")[1]))

        slogs = sorted(logs, key=lambda d: d[1], reverse=True)

        for j in slogs:
            ret["logs"].append({"container":j[0],"date":j[1],"block_duration":j[2],"scan_speed":j[3]})

        return json.dumps(ret)


    def get_container_from_name(self,name):
        for c in self.containers:
            if c.name == name: return c
        return None

    def refresh(self):
        threading.current_thread().name = "ContainersRefresh"

        while not self.refresh_thread_to_kill:
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
                cnt = self.get_container_from_name(sdr[i]['Names'])
                if cnt is None:
                    cnt = Container(sdr[i],pool,worker)
                    cnt.set_gpu_id()
                    self.containers.append(cnt)
                elif cnt.gpu_id is None:
                    cnt.set_gpu_id()

                try:
                    for item in get_command_output("docker exec -it "+sdr[i]['Names']+" bash -c 'cat /proc/`ps -A | grep BitCrack | awk \"{ print \\\$1 }\"`/environ | tr \"\\000\" \"\\n\"'",[]):
                        if item.startswith("POOL_NAME="): pool = item.split("=")[1]
                        if item.startswith("WORKER_NAME="): worker = item.split("=")[1]
                except Exception as e:
                    LOG.error("Exception : "+str(e))

                cnt.update(sdr[i],pool,worker)

            except Exception as e:
                LOG.error("Exception : "+str(e))

    def start_refresh_thread(self,interval):
        self.refresh_thread = threading.Thread(target = self.refresh)
        self.refresh_thread.start()

