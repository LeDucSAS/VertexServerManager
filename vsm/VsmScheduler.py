import logging
import schedule
from vsm.VsmData import VsmData
from vsm.VsmFileManager import VsmFileManager


logger = logging.getLogger("VsmScheduler")


class VsmScheduler():
    '''
    The scheduler purpose is to execute tasks
    There are 2 kind of tasks
    First one are permanent tasks, that are setup to be daily (ex: server restarts, check for updates, ...)
    Second one are exceptional tasks, that are to be executed once (ex: install a server, download a mod, ...)
    
    The scheduler checks permanent tasks
    '''

    def __init__(self):
        schedule.run_pending()
        ...


    @staticmethod
    def start():
        print("scheduler start")
        scheduler_data = VsmFileManager.read_conf_file("scheduler.yaml")
        scheduler_data["scheduler_active"] = True
        VsmFileManager.write_conf_file("scheduler.yaml", scheduler_data)


    @staticmethod
    def stop():
        print("scheduler stop")
        scheduler_data = VsmFileManager.read_conf_file("scheduler.yaml")
        scheduler_data["scheduler_active"] = False
        VsmFileManager.write_conf_file("scheduler.yaml", scheduler_data)

