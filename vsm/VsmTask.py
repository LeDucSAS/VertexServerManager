import logging
import uuid
from vsm.VsmTaskType import VsmTaskType


logger = logging.getLogger("VsmTask")


class VsmTask():

    def create(self, task_type:dict) -> dict:
        logger.debug(f"create_task( {task_type} )")
        bundle:dict = {}
        bundle["uuid"] = str(uuid.uuid4())

        if(task_type == VsmTaskType.CLEAR_CACHE):
            bundle["task"] = VsmTaskType.CLEAR_CACHE
        elif(task_type == VsmTaskType.CLEAR_TASKS_OK):
            bundle["task"] = VsmTaskType.CLEAR_TASKS_OK
        elif(task_type == VsmTaskType.CLEAR_TASKS_KO):
            bundle["task"] = VsmTaskType.CLEAR_TASKS_KO
        elif(task_type == VsmTaskType.CLEAR_TASKS_PROCESSED):
            bundle["task"] = VsmTaskType.CLEAR_TASKS_PROCESSED
        elif(task_type == VsmTaskType.CLEAR_TASKS_PENDING):
            bundle["task"] = VsmTaskType.CLEAR_TASKS_PENDING
        elif(task_type == VsmTaskType.CLEAR_TASKS_ALL):
            bundle["task"] = VsmTaskType.CLEAR_TASKS_ALL
        

        elif(task_type == VsmTaskType.MOD_INSTALL):
            bundle["task"] = VsmTaskType.MOD_INSTALL
            bundle["mod_url"] = None

        elif(task_type == VsmTaskType.SCHEDULER_START):
            bundle["task"] = VsmTaskType.SCHEDULER_START

        elif(task_type == VsmTaskType.SCHEDULER_STOP):
            bundle["task"] = VsmTaskType.SCHEDULER_STOP

        elif(task_type == VsmTaskType.SERVER_INSTALL):
            bundle["task"] = VsmTaskType.SERVER_INSTALL

        elif(task_type == VsmTaskType.SERVER_RESTART_BY_ID):
            bundle["task"] = VsmTaskType.SERVER_RESTART_BY_ID
            bundle["server_id"] = None

        elif(task_type == VsmTaskType.SERVER_RESTART_BY_LOCALNAME):
            bundle["task"] = VsmTaskType.SERVER_RESTART_BY_LOCALNAME
            bundle["server_localname"] = None

        elif(task_type == VsmTaskType.SERVER_START):
            bundle["task"] = VsmTaskType.SERVER_START
            bundle["server_id"] = None
            bundle["server_name"] = None
            bundle["server_port"] = None
            bundle["server_map"] = None
            bundle["server_mode"] = None

        elif(task_type == VsmTaskType.SERVER_STOP_BY_ID):
            bundle["task"] = VsmTaskType.SERVER_STOP_BY_ID
            bundle["server_id"] = None

        elif(task_type == VsmTaskType.SERVER_STOP_BY_LOCALNAME):
            bundle["task"] = VsmTaskType.SERVER_STOP_BY_LOCALNAME
            bundle["server_localname"] = None

        else:
            raise ValueError("VsmTask.create => Unknown VsmTaskType")
        
        return bundle