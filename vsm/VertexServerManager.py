import logging
import os
import psutil
import re
import signal
import subprocess
import time
from vsm.VsmFileManager import VsmFileManager
from vsm.VsmData import VsmData
from subprocess import CalledProcessError
from subprocess import check_output
from sys import platform


logger = logging.getLogger("VertexServerManager")


class VertexServerManager():

    def __init__(self):
        self.vfm = VsmFileManager()
        self.SERVER_PARAMS = VsmData().SERVER_DEFAULT


    """

    def __init__                            (self):
    def get_all_started_servers             (self): 
    def is_server_already_started           (self, server_localname):
    def is_folder_has_been_initialized      (self, directory_path=None):
    def get_current_highest_gameserver_id   (self, directory_path=None):
    def get_server_list_full_Path           (self, directory_path):
    def get_server_list_only_localname      (self, directory_path=None):
    def find_server_localname_by_id         (self, server_port):
    def start_server_by_localname           (self, server_localname):
    def start_server_by_id                  (self, server_port):
    def kill_server_by_localname            (self, server_localname):
    def kill_server_by_id                   (self, server_port):
    def restart_server_by_localname         (self, server_localname):
    def restart_server_by_id                (self, server_port):

    """


    def get_all_started_servers(self): 
        active_server_list = []

        if platform == "linux" or platform == "linux2":
            serverList = self.get_server_list_only_localname(os.getcwd())
            try:
                pidlist = check_output(["pidof","MCSServer"], universal_newlines=True).split()
            except CalledProcessError as e:
                pidlist = None

            if pidlist:
                if serverList is not None:
                    for pid in pidlist:
                        p = psutil.Process(int(pid))
                        if "MCSServer" in p.exe():
                            liveServerArgs = p.cmdline()
                            for arg in liveServerArgs:
                                if "-port=" in arg:
                                    server_port = arg.split("=")[1]
                                if "game=" in arg:
                                    server_mode = arg.split("=")[1]
                                if "?" in arg:
                                    server_map = arg.split("?")[0]
                                if "-servername=" in arg:
                                    server_gamename = arg.split("=")[1]
                            server_localname = p.exe().split('/')[-5]
                            server_data = {
                                "server_localname" : server_localname,
                                "server_pid"       : pid,
                                "server_mode"      : server_mode,
                                "server_map"       : server_map,
                                "server_port"      : server_port,
                                "server_gamename"  : server_gamename
                            }
                            active_server_list.append(server_data)

        elif platform == "win32":
            pidlist = check_output(
                ["WMIC", "path", "win32_process", "get", "Caption,Processid,Commandline"], 
                universal_newlines=True, 
                shell=True)
            lines = pidlist.splitlines(keepends=True)
            for line in lines:
                if "\\Win64\\MCSServer.exe" in line:
                    splitted_line = " ".join(line.replace("\\", "/").split()).split(" ")
                    if "MCSServer.exe" in splitted_line[0]:
                        serverpath = ""
                        for item in splitted_line:
                            if "/VertexServerManager/" in item:
                                serverpath = item
                        server_pid = splitted_line[-1]
                        server_localname = serverpath.split('/')[-5]
                        server_data = {
                            "server_localname" : server_localname,
                            "server_pid"       : server_pid,
                            "server_mode"      : splitted_line[2].split("=")[1],
                            "server_map"       : splitted_line[2].split("?")[0],
                            "server_port"      : splitted_line[3].split("=")[1],
                            "server_gamename"  : ' '.join(splitted_line[4:-1]).split("=")[1].replace("\"","").replace("'","")
                            # "server_gamename"  : ' '.join(splitted_line[4:-1]).split("=")[1][1:-2]
                        }
                        active_server_list.append(server_data)
        return active_server_list


    def is_server_already_started(self, server_localname):
        all_started_servers = self.get_all_started_servers()
        server_already_started = False
        if all_started_servers:
            for server in all_started_servers:
                if server_localname in server['server_localname']:
                    server_already_started = True
        return server_already_started


    ##########
    # GET INFORMATIONS


    def is_folder_has_been_initialized(self, directory_path=None):
        logger.debug("is_folder_has_been_initialized() ...")
        result = False
        if directory_path == None:
            directory_path = os.getcwd()

        if (
            os.path.exists(f"{directory_path}/maps")    and
            os.path.exists(f"{directory_path}/servers") and
            os.path.exists(f"{directory_path}/cache")
        ):
            result = True
        logger.debug(f"is_folder_has_been_initialized() returns {result}")
        return result


    def get_current_highest_gameserver_id(self, directory_path=None):
        logger.debug("get_current_highest_gameserver_id() ...")
        if directory_path == None:
            directory_path = os.getcwd()

        gameServerList = self.get_server_list_full_Path(directory_path)

        if gameServerList is None or not gameServerList:
            return None

        tmp = []
        for server in gameServerList:
            tmp.append(int(re.sub('[^0-9]','', server)))
        tmp.sort()
        result = int(tmp[-1])
        logger.debug(f"get_current_highest_gameserver_id() returns {result}")
        return result
    
    
    def get_server_list_full_Path(self, directory_path):
        logger.debug(f"get_server_list_full_Path() ...")
        result = None
        if self.is_folder_has_been_initialized():
            rootdir = f"{directory_path}/servers/"
            if os.listdir(rootdir): 
                gameServerList = []
                for file in os.listdir(rootdir):
                    d = os.path.join(rootdir, file)
                    if os.path.isdir(d):
                        gameServerList.append(d)
                result = gameServerList
        logger.debug(f"get_server_list_full_Path() returns {result}")
        return result


    def get_server_list_only_localname(self, directory_path=None):
        if directory_path == None:
            directory_path = os.getcwd()

        gameServerList = self.get_server_list_full_Path(directory_path)
        if gameServerList is not None:
            tmp = []
            for server in gameServerList:
                tmp.append(server.split("/")[-1])
            tmp.sort()
            return tmp
        else:
            return None


    def find_server_localname_by_id(self, server_port):
        directory_path = os.getcwd()
        serverList = self.get_server_list_only_localname(directory_path)
        has_server_localname_been_found = False
        if serverList is not None:
            for server_localname in serverList:
                if server_localname.endswith(str(server_port)):
                    has_server_localname_been_found = True
                    return server_localname
        if not has_server_localname_been_found:
            return None


    ##########
    # START SERVER
    def start_server_by_localname(self, server_localname):
        logger.info(f"    ->  Starting server {server_localname} ...")

        if int(self.SERVER_PARAMS['port']) < 1:
            self.SERVER_PARAMS['port'] = re.sub('[^0-9]','', server_localname)

        if platform == "linux" or platform == "linux2":
            server_binary_path = f"./servers/{server_localname}/MCS/Binaries/Linux/MCSServer"
        elif platform == "win32":
            server_binary_path = f"./servers/{server_localname}/MCS/Binaries/Win64/MCSServer.exe"
        
        server_binary_path = os.path.abspath(server_binary_path)
        argument_map      = self.SERVER_PARAMS['map']
        argument_gamemode = self.SERVER_PARAMS['mode']
        argument_port     = self.SERVER_PARAMS['port']
        argument_gamename = self.SERVER_PARAMS['name']

        if platform == "linux" or platform == "linux2":
            server_arguments = f"{argument_map}?game={argument_gamemode} -port={argument_port} -servername='{argument_gamename}'"
            server = subprocess.Popen([
                f"{server_binary_path} {server_arguments}"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
        elif platform == "win32":
            DETACHED_PROCESS = 0x00000008
            server = subprocess.Popen([
                server_binary_path, 
                f"{argument_map}?game={argument_gamemode}",
                f"-port={argument_port}",
                f"-servername='{argument_gamename}'"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=DETACHED_PROCESS,
            shell=True)
            time.sleep(6)

        logger.info(f"    ->  Server {server_localname} has been started")
        logger.info(f"    ->    Port      - {argument_port}")
        logger.info(f"    ->    Game name - {argument_gamename}")
        logger.info(f"    ->    Mode      - {argument_gamemode}")
        logger.info(f"    ->    Map       - {argument_map}")
        return server.pid


    def start_server_by_id(self, server_port):
        server_localname = self.find_server_localname_by_id(server_port)

        if server_localname is not None:
            if not self.is_server_already_started(server_localname):
                server_pid = self.start_server_by_localname(server_localname)
                logger.info(f"    ->  Server {server_localname} started with pid {server_pid}")
            else:
                logger.info(f"    ->  Server {server_localname} already started.")
        else:
            logger.info(f"    ->  No server found with id {server_port}")


    ##########
    # STOP SERVER 
    def kill_server_by_localname(self, server_localname):
        logger.info(f"    ->  {server_localname} shutting down server ...")

        server_is_active = self.is_server_already_started(server_localname)
        if not server_is_active:
            logger.info(f"    ->  {server_localname} server is not currently active.")
            return

        errorNoServer = False
        # First SIGINT
        try:
            all_started_servers = self.get_all_started_servers()
            if all_started_servers:
                for server in all_started_servers:
                    if server_localname in server['server_localname']:
                        os.kill(int(server['server_pid']), signal.SIGINT)
        except subprocess.CalledProcessError as e:
            errorNoServer = True

        if errorNoServer:
            logger.info("Warning : No server found, no shutdown")
            return

        # Wait for shutdown before the second SIGINT
        time.sleep(6)

        # Second SIGINT (as sometimes it is required for reasons I don't explain)
        try:
            all_started_servers = self.get_all_started_servers()
            if all_started_servers:
                for server in all_started_servers:
                    if server_localname in server['server_localname']:
                        os.kill(int(server['server_pid']), signal.SIGINT)
        except subprocess.CalledProcessError as e:
            logger.info("Info : No server found on second SIGINT, seems server has been killed on first SIGINT")

        # Check that server is shutdown (don't use psutil because I want to check the path)
        try:
            serverDed = True
            all_started_servers = self.get_all_started_servers()
            if all_started_servers:
                for server in all_started_servers:
                    if server_localname in server['server_localname']:
                        logger.info("Warning : Server still alive")
                        serverDed = False
            if serverDed:
                logger.info(f"    ->  Server {server_localname} has been shutdown")
        except subprocess.CalledProcessError as e:
            logger.info(f"    ->  Server {server_localname} has been shutdown")


    def kill_server_by_id(self, server_port):
        server_localname = self.find_server_localname_by_id(server_port)

        if server_localname is not None:
            logger.info(f"Killing server {server_localname}...")
            server_pid = self.kill_server_by_localname(server_localname)
            logger.debug(f"Killed PID {server_pid}")
        else:
            logger.info(f"No server found with id {server_port}")


    # RESTART
    def restart_server_by_localname(self, server_localname):
        fullServerList = self.get_server_list_only_localname(os.getcwd())
        if fullServerList is not None:
            startedServerList = self.get_all_started_servers()
            for startedServer in startedServerList:
                if server_localname in startedServer["server_localname"]:
                    self.SERVER_PARAMS['port'] = startedServer["server_port"]
                    self.SERVER_PARAMS['mode'] = startedServer["server_mode"]
                    self.SERVER_PARAMS['map']  = startedServer["server_map"]
                    self.SERVER_PARAMS['name'] = startedServer["server_gamename"]

                    self.kill_server_by_localname(server_localname)
                    time.sleep(1)
                    self.start_server_by_localname(server_localname)
        else:
            logger.info("No server installed.")


    def restart_server_by_id(self, server_port):
        self.restart_server_by_localname(self.find_server_localname_by_id(server_port))

