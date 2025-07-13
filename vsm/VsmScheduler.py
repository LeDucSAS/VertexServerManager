import logging
import schedule
import time
import os
from os import listdir
from os.path import isfile, join
from vsm.VsmFileManager import VsmFileManager
from vsm.VertexServerManager import VertexServerManager
from vsm.VsmTask import VsmTask
from vsm.VsmTaskExecutor import VsmTaskExecutor
from vsm.VsmTaskType import VsmTaskType


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
        self.heartbeat_filename = "scheduler_heartbeat.yaml"

        # Setup automatic scheduling
        def basic_restart_all_servers():
            for server_localname in VertexServerManager.get_server_list_only_localname(os.getcwd()): 
                do_server_restart_by_localname = VsmTask().create(VsmTaskType.SERVER_RESTART_BY_LOCALNAME)
                do_server_restart_by_localname["server_localname"] = server_localname
                VsmFileManager.write_task_file(do_server_restart_by_localname)

        schedule.every().day.at("2:30").do(basic_restart_all_servers)
        # Overwrite heartbeat
        VsmFileManager.write_conf_file(self.heartbeat_filename, {"test_value": 0})


    def start_loop(self):
        while(VsmFileManager.read_conf_file("scheduler.yaml")["scheduler_active"]):
            # Pace execution time
            time.sleep(1)
            # Update heartbeat
            self.heartbeat()
            # Check for task files
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
            # Execute pending tasks
            schedule.run_pending()


    def heartbeat(self):
        # if number is going up, then scheduler is active
        test_data = VsmFileManager.read_conf_file(self.scheduler_tracking)
        if(test_data["test_value"] == 100):
            test_data["test_value"] = 0
        else:
            test_data["test_value"] = test_data["test_value"] + 1
        VsmFileManager.write_conf_file(self.scheduler_tracking, test_data)

