import logging


logger = logging.getLogger("VsmTaskType")


class VsmTaskType():
    CLEAR_CACHE = "clear_cache"
    CLEAR_TASKS_OK = "clear_tasks_ok"
    CLEAR_TASKS_KO = "clear_tasks_ko"
    CLEAR_TASKS_ALL = "clear_tasks_all"
    CLEAR_TASKS_PENDING = "clear_tasks_pending"
    CLEAR_TASKS_PROCESSED = "clear_tasks_processed"
    CREATE_SERVER_FOLDER_STRUCTURE = "create_vsm_folder_structure"
    MOD_INSTALL = "mod_install"
    SCHEDULER_START = "scheduler_start"
    SCHEDULER_STOP = "scheduler_stop"
    SERVER_INSTALL = "server_install"
    SERVER_RESTART_BY_ID = "server_restart_by_id"
    SERVER_RESTART_BY_LOCALNAME = "server_restart_by_localname"
    SERVER_START = "server_start"
    SERVER_STOP_BY_ID = "server_stop_by_id"
    SERVER_STOP_BY_LOCALNAME = "server_stop_by_localname"