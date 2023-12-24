import sys
import re
from datetime import datetime
from threading import RLock,currentThread
from inspect import currentframe

class LEVEL():
    debug = 10
    info = 20
    warning = 30
    error = 40
    fatal = 50
    temp = 100
    
    @staticmethod
    def Str(level):
        if level == LEVEL.fatal:
            return "▲FATAL"
        elif level == LEVEL.error:
            return "△ERROR"
        elif level == LEVEL.warning:
            return "●WARN"
        elif level == LEVEL.info:
            return " INFO"
        elif level == LEVEL.debug:
            return " DEBUG"
        elif level == LEVEL.temp:
            return "○TEMP"
        else:
            return "UNDEF"

# TODO migrate to a driver

class Logger():
    instance = None
    def __init__(self):
        if Logger.instance is not None:
            raise Exception("Logger singleton already exist")
        else:
            Logger.instance = self
            Logger.instance.dolog = False
            Logger.instance.level = LEVEL.debug
            Logger.instance.custom_callback = []
            Logger.instance.lock = RLock()

    @staticmethod
    def Get():
        if Logger.instance is None:
            Logger()
        return Logger.instance
  
    def log(self,level,obj):
        if Logger.instance.dolog and Logger.instance.level <= level:
            frame = currentframe()
            #while frame.f_back is not None and frame.f_back.f_code.co_filename.find('Logger') != -1: 
            while frame.f_back is not None and frame.f_back.f_code.co_filename.find('log.py') != -1: 
                frame = frame.f_back
            if frame.f_back is not None: 
                frame = frame.f_back
            line_nb = str(frame.f_lineno)
            file_name = re.sub(r'^.*SimpleBlockchain[/\\]',"",frame.f_code.co_filename)
            with Logger.instance.lock:
                log_str = "{:26} {:7s} {:12s} ".format(str(datetime.now()),LEVEL.Str(level),currentThread().getName()) + file_name + ":" + line_nb + " " + str(obj).replace('\n','\\n')
                print(log_str)
                for cb in Logger.instance.custom_callback: 
                    try:
                        cb[0](log_str,cb[1])                       # custom callback : file , udp console ...    cb is a 2-uple of (callback,parameters)
                    except  Exception as e:
                        Logger.instance.custom_callback.remove(cb)
                        LOG.warning("Exception in custom callback , unregistering : "+str(e))
            sys.stdout.flush()
                        
            
class LOG():
    @staticmethod
    def register_cb(callback_def_tuple):
        Logger.Get().custom_callback.append(callback_def_tuple)

    @staticmethod
    def start():
        Logger.Get().dolog = True

    @staticmethod
    def stop():
        Logger.Get().dolog = False

    @staticmethod
    def level(level):
        Logger.Get().level = level
    
    @staticmethod
    def debug(obj):
        Logger.Get().log(LEVEL.debug,obj)
    
    @staticmethod
    def info(obj):
        Logger.Get().log(LEVEL.info,obj)

    @staticmethod
    def warning(obj):
        Logger.Get().log(LEVEL.warning,obj)

    @staticmethod
    def error(obj):
        Logger.Get().log(LEVEL.error,obj)

    @staticmethod
    def fatal(obj):
        Logger.Get().log(LEVEL.fatal,obj)

    @staticmethod
    def temp(obj):
        Logger.Get().log(LEVEL.temp,obj)

