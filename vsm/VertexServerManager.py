import copy
import logging
import os
import psutil
import re
import requests
import signal
import stat
import subprocess
import time
import vsm.VsmFileManager as VsmFileManager
from subprocess import CalledProcessError
from subprocess import check_output
from sys import platform
from urllib.request import urlopen


logger = logging.getLogger("VertexServerManager")


class VertexServerManager():
    def __init__(self):
        self.vfm = VsmFileManager.VsmFileManager()


    """

    Class Structure
    -- Global data
    Data
    def __init__(self):
    
    -- Base functions
    def is_folder_has_been_initialized    (self, directory_path=None):
    def get_all_started_servers           (self):
    def is_server_already_started         (self, server_localname):
    def create_symlink                    (self, symlink_source_path, symlink_target_path):
    def get_server_list_full_Path         (self, directory_path):
    def get_server_list_only_localname    (self, directory_path=None):
    def find_server_localname_by_id       (self, server_port):
    def get_current_highest_gameserver_id (self, directory_path=None):
    def start_server_by_localname         (self, server_localname):
    def start_server_by_id                (self, server_port):
    def kill_server_by_localname          (self, server_localname):
    def kill_server_by_id                 (self, server_port):
    def restart_server_by_localname       (self, server_localname):
    def restart_server_by_id              (self, server_port):
    
    -- Global functions
    def create_server_folder_structure    (self, server_init_path=None):
    def download_file_to_cache            (self, url_to_download):
    def install_linux_game_server         (self, choosen_version=None):

    """


    '''


    Global data


    '''


    DATA = {}

    DATA['playVertexRoot']              = "https://www.playvertex.com"
    DATA['filekPatchHostLinuxLatest']   = f"{DATA['playVertexRoot']}/patchhostlinux"
    DATA['filekPatchHostWindowsLatest'] = f"{DATA['playVertexRoot']}/patchhostwindows"
    DATA['filePatchLatest']             = f"{DATA['playVertexRoot']}/patch"
    DATA['fileVertexServerFullWindows'] = f"{DATA['playVertexRoot']}/download/files/Vertex_Server_Windows_<VERSION>.zip"
    DATA['fileVertexServerFullLinux']   = f"{DATA['playVertexRoot']}/download/files/Vertex_Server_Linux_<VERSION>.tar.gz"

    DATA['apiRoot']             = "https://api.playvertex.com"
    DATA['apiServers']          = f"{DATA['apiRoot']}/servers"
    DATA['apiStats']            = f"{DATA['apiRoot']}/stats"
    DATA['apiVersion']          = f"{DATA['apiRoot']}/version"

    DATA['server_localnameTemplate'] = "GameServer<NUMBER>"
    DATA['defaultStartingPort'] = 27070

    DATA['gameServerMap']       = "P_FFA_COMPLEX"
    DATA['gameServerMode']      = "OPEN"
    DATA['gameServer_port']     = -1
    DATA['gameServer_gamename'] = "Vertex Server"




    '''


    Base functions


    '''


    ##########
    # CHECK THINGS
    def is_folder_has_been_initialized(self, directory_path=None):
        if directory_path == None:
            directory_path = os.getcwd()

        if (
            os.path.exists(f"{directory_path}/maps")    and
            os.path.exists(f"{directory_path}/servers") and
            os.path.exists(f"{directory_path}/cache")
        ):
            return True
        else:
            return False


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


    def create_symlink(self, symlink_source_path, symlink_target_path):
        os.symlink(
            os.path.abspath(symlink_source_path), 
            os.path.abspath(symlink_target_path)
        )
        return True


    ##########
    # GET INFORMATIONS
    def get_server_list_full_Path(self, directory_path):
        if self.is_folder_has_been_initialized():
            rootdir = f"{directory_path}/servers/"
            if os.listdir(rootdir): 
                gameServerList = []
                for file in os.listdir(rootdir):
                    d = os.path.join(rootdir, file)
                    if os.path.isdir(d):
                        gameServerList.append(d)
                return gameServerList
        else:
            return None


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


    def get_current_highest_gameserver_id(self, directory_path=None):
        if directory_path == None:
            directory_path = os.getcwd()

        gameServerList = self.get_server_list_full_Path(directory_path)

        if gameServerList is None or not gameServerList:
            return None

        tmp = []
        for server in gameServerList:
            tmp.append(int(re.sub('[^0-9]','', server)))
        tmp.sort()
        return int(tmp[-1])


    ##########
    # START SERVER
    def start_server_by_localname(self, server_localname):
        logger.info(f"    ->  Starting server {server_localname} ...")

        if int(self.DATA['gameServer_port']) < 1:
            self.DATA['gameServer_port'] = re.sub('[^0-9]','', server_localname)

        if platform == "linux" or platform == "linux2":
            serverBinaryPath = f"./servers/{server_localname}/MCS/Binaries/Linux/MCSServer"
        elif platform == "win32":
            serverBinaryPath = f"./servers/{server_localname}/MCS/Binaries/Win64/MCSServer.exe"
        
        serverBinaryPath = os.path.abspath(serverBinaryPath)
        argument_map = self.DATA['gameServerMap']
        argument_gamemode = self.DATA['gameServerMode']
        argument_port = self.DATA['gameServer_port']
        argument_gamename = self.DATA['gameServer_gamename']

        if platform == "linux" or platform == "linux2":
            server_arguments = f"{argument_map}?game={argument_gamemode} -port={argument_port} -servername='{argument_gamename}'"
            server = subprocess.Popen([
                f"{serverBinaryPath} {server_arguments}"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
        elif platform == "win32":
            DETACHED_PROCESS = 0x00000008
            server = subprocess.Popen([
                serverBinaryPath, 
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
        logger.info(f"    ->  Shutdowning server {server_localname} ...")

        server_is_active = self.is_server_already_started(server_localname)
        if not server_is_active:
            logger.info(f"    ->  Server {server_localname} is not currently active.")
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
        else:
            logger.info(f"No server found with id {server_port}")


    # RESTART
    def restart_server_by_localname(self, server_localname):
        fullServerList = self.get_server_list_only_localname(os.getcwd())
        if fullServerList is not None:
            startedServerList = self.get_all_started_servers()
            for startedServer in startedServerList:
                if server_localname in startedServer["server_localname"]:
                    self.DATA['gameServer_port'] = startedServer["server_port"]
                    self.DATA['gameServerMode'] = startedServer["server_mode"]
                    self.DATA['gameServerMap'] = startedServer["server_map"]
                    self.DATA['gameServer_gamename'] = startedServer["server_gamename"]

                    self.kill_server_by_localname(server_localname)
                    time.sleep(1)
                    self.start_server_by_localname(server_localname)
        else:
            logger.info("No server installed.")


    def restart_server_by_id(self, server_port):
        self.restart_server_by_localname(self.find_server_localname_by_id(server_port))




    '''


    Global functions


    '''


    def create_server_folder_structure(self, server_init_path=None):
        if server_init_path is None:
            server_init_path = os.getcwd()

        logger.info("Check that path has not been initialized already.")
        if not self.is_folder_has_been_initialized():
            map_folder_path    = f"{server_init_path}/maps"
            server_folder_path = f"{server_init_path}/servers"
            cache_folder_path  = f"{server_init_path}/cache"

            folders_to_create = []
            folders_to_create.append(map_folder_path)
            folders_to_create.append(server_folder_path)
            folders_to_create.append(cache_folder_path)

            for ftc in folders_to_create:
                if not os.path.exists(ftc):
                    logger.info(f"    Creating - {ftc}")
                    os.makedirs(ftc)
                else:
                    logger.info(f"    Already exists - {ftc}")

            logger.info("    ->  Current directory has been init for vertex servers.")
        else:
            logger.info("    ->  Seems directory has already been initialized")
            logger.info("    ->  Please check for existence for the fallowing folders")
            logger.info("            ./maps/")
            logger.info("            ./servers/")
            logger.info("            ./cache/")
            logger.info("            ./vsm/")
            logger.info("    ->  If init has failed, please remove all folders but ./vsm/")
            logger.info("    ->  Init will stop")


    def download_file_to_cache(self, url_to_download):
        filename = url_to_download.split("/")[-1:][0]
        cache_file_path = f"cache/{filename}"
        # Download from URL
        with urlopen(url_to_download) as file:
            content = file.read()
        # Save to file
        with open(cache_file_path, 'wb') as download:
            download.write(content)
        return cache_file_path


    def install_game_server(self, choosen_version=None):
        global DATA
        
        if platform == "linux" or platform == "linux2":
            ...
        elif platform == "darwin":
            logger.info("OSX not supported right now currently")
        elif platform == "win32":
            ...

        if choosen_version is None:
            response = requests.get(self.DATA['apiVersion'])
            choosen_version = response.json()['version']
        
        if platform == "linux" or platform == "linux2":
            url_to_download = copy.copy(self.DATA['fileVertexServerFullLinux']).replace("<VERSION>", choosen_version)
        elif platform == "win32":
            url_to_download = copy.copy(self.DATA['fileVertexServerFullWindows']).replace("<VERSION>", choosen_version)
        

        ############################################################
        # Check init, download, unzip, clean cache
        folder_has_been_init = self.is_folder_has_been_initialized(os.getcwd())
        if not folder_has_been_init:
            logger.info("Warning : Folder has not been init, script will stop.")
            logger.info("You can init the folder doing like : python ./vsm.py --init")
            return

        logger.info("Downloading server archive to ./cache/ ...")
        downloaded_file_path = self.download_file_to_cache(url_to_download)
        logger.info("    ->  Done")

        logger.info("Extracting server archive file into ./cache/")
        
        if platform == "linux" or platform == "linux2":
            self.vfm.untargz_file(downloaded_file_path, './cache')
        elif platform == "win32":
            self.vfm.unzip_file(downloaded_file_path, './cache')
        
        logger.info("    ->  Done")

        logger.info("Deleting downloaded file from ./cache/")
        self.vfm.remove_at_path(downloaded_file_path)
        logger.info("    ->  Done")
        

        ############################################################
        # Define new server identity
        new_server_number = self.get_current_highest_gameserver_id()
        if new_server_number is None:
            new_server_number = self.DATA['defaultStartingPort']
        else:
            new_server_number += 1
        new_server_localname = copy.copy(self.DATA['server_localnameTemplate']).replace("<NUMBER>", str(new_server_number))
        logger.info(f"New server name will be : {new_server_localname}")
        
        # Move files
        logger.info("Move server file to ./servers/")
        
        if platform == "linux" or platform == "linux2":
            server_source = "./cache/launcher/files/mcs_server_linux/Server"
        elif platform == "win32":
            server_source = "./cache/Server"
        
        server_destination = f"./servers/{new_server_localname}"
        self.vfm.move_folder(server_source, server_destination)
        logger.info("    ->  Done")


        ############################################################
        # Remove useless files from cache
        
        if platform == "linux" or platform == "linux2":
            logger.info("Clean ./cache/ from useless files")
            self.vfm.remove_at_path('./cache/launcher/')
            logger.info("    ->  Done")

        
        ############################################################
        # Make server binary executable
        if platform == "linux" or platform == "linux2":
            linux_binary = f"./servers/{new_server_localname}/MCS/Binaries/Linux/MCSServer"
            st = os.stat(linux_binary)
            os.chmod(linux_binary, st.st_mode | stat.S_IEXEC)


        ############################################################
        # Start server
        logger.info("Make first server start to generate conf files etc.")
        server_pid = self.start_server_by_localname(new_server_localname)

        if psutil.pid_exists(server_pid):
            logger.info("    ->  Server has started correctly")

        # Wait for init to end
        logger.info("Waiting 6 seconds to let server do his init")
        time.sleep(6)
        logger.info("    ->  Done")

        # Checking that server is alive as expected
        if not psutil.pid_exists(server_pid):
            logger.info("!!!!! Server is not alive, something might be wrong !!!!!")


        ############################################################
        # Kill the server nicely to force save of config files

        logger.info("Shutting down the server properly")
        self.kill_server_by_localname(new_server_localname)


        ############################################################
        # Make symlink to add map folder to gameserver to optimize spacedisk
        logger.info("Make symlink of ./maps/ inside UserCreatedContent")
        # That is the part that requires having Admin rights
        symlink_has_been_created = self.create_symlink("./maps/", f"./servers/{new_server_localname}/MCS/UserCreatedContent/maps/")
        if symlink_has_been_created:
            logger.info("    ->  Done")
        else:
            logger.info("    ->  Error")
        logger.info("\n----------\n")
        logger.info(f"Server installation has finished for {new_server_localname}.")
        logger.info("\n----------\n")

