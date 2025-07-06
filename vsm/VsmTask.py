import logging
import uuid
from vsm.VsmTaskType import VsmTaskType


logger = logging.getLogger("VsmTask")


class VsmTask():

    def create(self, task_type):
        logger.debug(f"create_task( {task_type} )")
        bundle = {}
        bundle["id"] = uuid.uuid4()

        if(task_type == VsmTaskType.CACHE_CLEANUP):
            bundle["task"] = VsmTaskType.CACHE_CLEANUP
            # No other data is required

        if(task_type == VsmTaskType.MOD_INSTALL):
            bundle["task"] = VsmTaskType.MOD_INSTALL
            bundle["mod_url"] = None

        if(task_type == VsmTaskType.SERVER_INSTALL):
            bundle["task"] = VsmTaskType.SERVER_INSTALL
            bundle["server_id"] = None

        if(task_type == VsmTaskType.SERVER_RESTART_BY_ID):
            bundle["task"] = VsmTaskType.SERVER_RESTART_BY_ID
            bundle["server_id"] = None

        if(task_type == VsmTaskType.SERVER_RESTART_BY_LOCALNAME):
            bundle["task"] = VsmTaskType.SERVER_RESTART_BY_LOCALNAME
            bundle["server_localname"] = None

        if(task_type == VsmTaskType.SERVER_START):
            bundle["task"] = VsmTaskType.SERVER_START
            bundle["server_id"] = None
            bundle["server_name"] = None
            bundle["server_port"] = None
            bundle["server_map"] = None
            bundle["server_mode"] = None

        if(task_type == VsmTaskType.SERVER_STOP_BY_ID):
            bundle["task"] = VsmTaskType.SERVER_STOP_BY_ID
            bundle["server_id"] = None

        if(task_type == VsmTaskType.SERVER_STOP_BY_LOCALNAME):
            bundle["task"] = VsmTaskType.SERVER_STOP_BY_LOCALNAME
            bundle["server_id"] = None

        return bundle