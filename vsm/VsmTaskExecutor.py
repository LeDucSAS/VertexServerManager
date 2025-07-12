import ctypes
import logging
import os
import sys
from sys import platform
import yaml
from vsm.ModioDownloadManager import ModioDownloadManager
from vsm.VertexServerInstaller import VertexServerInstaller
from vsm.VertexServerManager import VertexServerManager
from vsm.VsmFileManager import VsmFileManager
from vsm.VsmTaskType import VsmTaskType


logger = logging.getLogger("VsmTaskExecutor")


class VsmTaskExecutor():

    def __init__(self):
        self.vsi = VertexServerInstaller()
        self.vsm = VertexServerManager()


    def execute(self, task:dict) -> None:
        task_type = task["task"]
        if(task_type == VsmTaskType.CLEAR_CACHE):
            VsmFileManager.clear_cache()

        elif(task_type == VsmTaskType.CREATE_SERVER_FOLDER_STRUCTURE):
            self.vsi.create_server_folder_structure()

        elif(task_type == VsmTaskType.MOD_INSTALL):
            self.__install_mod(task["mod_url"])

        elif(task_type == VsmTaskType.SCHEDULER_START):
            self.__scheduler_switch_on()

        elif(task_type == VsmTaskType.SCHEDULER_STOP):
            self.__scheduler_switch_off()

        elif(task_type == VsmTaskType.SERVER_INSTALL):
            self.__game_server_install()

        elif(task_type == VsmTaskType.SERVER_STOP_BY_ID):
            self.__game_server_stop_by_id(task["server_id"])

        elif(task_type == VsmTaskType.SERVER_STOP_BY_LOCALNAME):
            self.__game_server_stop_by_localname(task["server_localname"])

        elif(task_type == VsmTaskType.SERVER_START):
            self.__game_server_start(task)

        elif(task_type == VsmTaskType.SERVER_RESTART_BY_ID):
            self.__game_server_restart_by_id(task["server_id"])

        elif(task_type == VsmTaskType.SERVER_RESTART_BY_LOCALNAME):
            self.__game_server_restart_by_localname(task["server_localname"])

        else:
            raise ValueError(f"VsmTaskExecutor.execute => The task type '{task_type}' is not a valid VsmTaskType")


    # Mod install
    def __install_mod(self, mod_url:str) -> None:
        if os.path.isfile('./conf/modio.yaml'):
            with open('./conf/modio.yaml', 'r') as file:
                modio_config = yaml.safe_load(file)
            mdm = ModioDownloadManager(modio_config)
            mdm.mod_install_direct_url(mod_url)
        else:
            logger.error("Please check ./conf/ folder, and create a modio.yaml file from template and add your api key into it.")


    # Scheduler
    def __scheduler_switch_on(self) -> None:
        VsmTaskExecutor.start()


    def __scheduler_switch_off(self) -> None:
        VsmTaskExecutor.stop()


    # Server start/stop/restart
    def __game_server_start(self, server_data:dict) -> None:
        if server_data["server_name"]:
            self.vsm.SERVER_PARAMS['name'] = server_data["server_name"]
        if server_data["server_port"] is not None:
            if server_data["server_port"] > 0:
                self.vsm.SERVER_PARAMS['port'] = server_data["server_port"]
        if server_data["server_map"]:
            self.vsm.SERVER_PARAMS['map'] = server_data["server_map"]
        if server_data["server_mode"]:
            self.vsm.SERVER_PARAMS['mode'] = server_data["server_mode"]
        self.vsm.start_server_by_id(server_data["server_id"])


    def __game_server_restart_by_localname(self, server_localname_to_restart:str) -> None:
        self.vsm.restart_server_by_localname(server_localname_to_restart)


    def __game_server_stop_by_id(self, server_id_to_stop:str) -> None:
        self.vsm.kill_server_by_id(server_id_to_stop)


    def __game_server_stop_by_localname(self, server_localname_to_stop:str) -> None:
        self.vsm.kill_server_by_localname(server_localname_to_stop)


    def __game_server_restart_by_id(self, server_id_to_restart:str) -> None:
        self.vsm.restart_server_by_id(server_id_to_restart)


    # Server install
    def __game_server_install(self) -> None:
        if platform == "linux" or platform == "linux2":
            self.vsi.install_game_server()
        elif platform == "win32":
            # Need to execute as admin because of symbolic linking map folder.
            print("\n")
            print("Windows script initialization need to execute as admin because of symbolic linking map folder.")
            print("Basically, it link once a common './maps/' to './servers/GameServerXXXXX/UserCreatedContent/maps/'.")
            print("Anything in ./maps/ folder is common to all other servers and do not need to dupplicates.")
            print("\n")

            def is_admin():
                try:
                    is_admin_value = ctypes.windll.shell32.IsUserAnAdmin()
                    if not is_admin_value:
                        print("Script will now ask for admin privilege.\n")
                        input("Press ENTER to continue or CTRL+C to exit.\n\n")
                    return is_admin_value
                except:
                    return False

            if is_admin():
                print("---------------------------\n")
                print("Vertex MCS Server installation procedure starts.\n")
                try:
                    self.vsi.install_game_server()
                except:
                    input("\nAn error occured. Press enter to exit script.")

                input("\nCourtesy input action to read logs.\nPress enter to terminate the script whenever you want.\n\n")
            else:
                # Re-run the program with admin rights
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


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

