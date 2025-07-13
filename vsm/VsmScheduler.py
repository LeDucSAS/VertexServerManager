import logging
import schedule
import time
import os
from os import listdir
from os.path import isfile, join
from vsm.VsmFileManager import VsmFileManager
from vsm.VsmTaskExecutor import VsmTaskExecutor


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
        self.executor = VsmTaskExecutor()
        self.task_path = "./tasks/"
        self.scheduler_tracking = "scheduler_heartbeat.yaml"
        VsmFileManager.write_conf_file(self.scheduler_tracking, {"test_value": 0})
        schedule.run_pending()

    def start_loop(self):
        while(VsmFileManager.read_conf_file("scheduler.yaml")["scheduler_active"]):
            time.sleep(1)
            self.iterate()
            onlyfiles = [f for f in listdir(self.task_path) if isfile(join(self.task_path, f))]
            onlyyaml = [f for f in onlyfiles if f.endswith(".yaml")]
            for task_filename in onlyyaml:
                task_file_path = os.path.abspath(f"{self.task_path}{task_filename}")
                try:
                    self.executor.execute(VsmFileManager.read_task_file(task_filename))
                    os.rename(task_file_path, os.path.abspath(f"{self.task_path}/ok/{task_filename}"))
                except:
                    os.rename(task_file_path, os.path.abspath(f"{self.task_path}/ko/{task_filename}"))
                break
            logger.debug("loop")

    def iterate(self):
        # if number is going up, then scheduler is active
        test_data = VsmFileManager.read_conf_file(self.scheduler_tracking)
        if(test_data["test_value"] == 100):
            test_data["test_value"] = 0
        else:
            test_data["test_value"] = test_data["test_value"] + 1
        VsmFileManager.write_conf_file(self.scheduler_tracking, test_data)
