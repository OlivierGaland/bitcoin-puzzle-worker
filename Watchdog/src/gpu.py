import time,threading
from tool import get_command_output
from log import LOG

class GpuState():
    def __init__(self,timestamp,smi_line):
        self.timestamp = timestamp
        self.temperature = float(smi_line[0])
        self.power = float(smi_line[1].split(" ")[0])
        self.power_limit = float(smi_line[2].split(" ")[0])
        self.mem_clock = float(smi_line[6].split(" ")[0])
        self.gpu_clock = float(smi_line[7].split(" ")[0])
        self.fan_speed = float(smi_line[8].split(" ")[0])
        self.mem_left = float(smi_line[11].split(" ")[0])
        self.gpu_usage = float(smi_line[12].split(" ")[0])
        self.mem_usage = float(smi_line[13].split(" ")[0])

class Gpu():
    def __init__(self,smi_line):
        if smi_line[9] != "Enabled": raise Exception("GPU presistence mode not enabled : "+smi_line[9])
        self.name = smi_line[3]
        self.uuid = smi_line[4]
        self.device_id = smi_line[5]
        self.total_memory = float(smi_line[10].split(" ")[0])
        self.dead = False
        self.history = dict()
        self.set_state(time.time(),smi_line)

    def set_state(self,ts,smi_line):
        self.state = GpuState(ts,smi_line)
        #self.history[ts] = self.state       #TODO : manage history

    def update(self,smi_line):
        if len(smi_line) == 14: 
            self.set_state(time.time(),smi_line)
        else:
            self.dead = True

    def to_html(self,idx,state):
        warnings,is_warnings = self.get_warnings()
        ret = "<tr"+(" class='highlight'" if is_warnings else "")+"><td>"+str(idx)+"</td><td>"+str(self.name)+"</td><td>"+str(self.total_memory)+" MB</td><td>"+str(int(100*(self.total_memory-state.mem_left)/self.total_memory))+" %</td><td>"+ str(int(state.gpu_usage))+ \
                    " %</td><td>"+str(int(state.temperature))+" C</td><td>"+str(int(state.fan_speed))+" %</td><td>"+str(int(state.mem_clock))+" Mhz</td><td>"+str(int(state.gpu_clock))+" Mhz</td><td>"+str(int(state.power_limit))+" W</td><td>"+str(state.power)+ \
                    " W</td><td>"+str(warnings)+"</td><tr>"
        return ret
    
    def get_warnings(self):
        ret = ""
        if self.dead: return "DEAD", True
        if self.state.temperature > 70: ret += "TEMP "
        if (self.state.power_limit/self.state.power) > 1.5: ret += "PWR "
        if ret == "": ret = "OK"
        return ret, (ret != "OK")

class GpuFactory():
    def __init__(self,count):
        self.count = count
        self.gpus = list()
        if get_command_output('nvidia-smi --query-gpu=count --format=csv')[0] != str(count): raise Exception("Invalid gpu count : "+str(count))
        self.init_gpus()
        self.refresh_thread = None

    def __del__(self):
        if self.refresh_thread != None: self.refresh_thread.join()

    def init_gpus(self):
        q = get_command_output('nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit,name,uuid,pci.sub_device_id,clocks.mem,clocks.gr,fan.speed,persistence_mode,memory.total,memory.free,utilization.gpu,utilization.memory --format=csv')
        if len(q) != self.count: raise Exception("Invalid gpu count in snapshot : "+str(self.count)+" != "+str(len(q)))
        for i in range(0,self.count): self.gpus.append(Gpu(q[i].split(", ")))


    def to_html(self):
        ret = "<table id='gpus_tab' class='bordered'><tr class='header'><th>Gpu</th><th>Name</th><th>Memory</th><th>Mem load</th><th>Gpu load</th><th>Temp</th><th>Fan speed</th><th>Mem clock</th><th>Gpu clock</th><th>Pwr limit</th><th>Pwr usage</th><th></th></tr>"
        for i in range(self.count): ret += self.gpus[i].to_html(i,self.gpus[i].state)
        return ret+ "</table>"

    def refresh(self):
        threading.current_thread().name = "GpusRefresh"

        while True:
            time.sleep(10)
            LOG.info("Refreshing")
            self.refresh_allgpus()

    def get_gpu_from_id(self,uuid):
        for g in self.gpus:
            if g.uuid == uuid: return g

    def refresh_allgpus(self):
        q = get_command_output('nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit,name,uuid,pci.sub_device_id,clocks.mem,clocks.gr,fan.speed,persistence_mode,memory.total,memory.free,utilization.gpu,utilization.memory --format=csv')

        if len(q) != self.count:
            q = list()
            for i in range(self.count):
                q.append(get_command_output('nvidia-smi -i '+str(i)+' --query-gpu=temperature.gpu,power.draw,power.limit,name,uuid,pci.sub_device_id,clocks.mem,clocks.gr,fan.speed,persistence_mode,memory.total,memory.free,utilization.gpu,utilization.memory --format=csv')[0])

        for i in range(len(q)):
            qs = q[i].split(", ")
            self.get_gpu_from_id(qs[4]).update(qs)            

    def start_refresh_thread(self,interval):
        self.refresh_thread = threading.Thread(target = self.refresh)
        self.refresh_thread.start()

        #webserver_thread = threading.Thread(target = WebserverThread)
        #webserver_thread.start()
