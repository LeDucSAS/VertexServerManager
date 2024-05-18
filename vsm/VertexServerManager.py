class VertexServerManager():
    def __init__(self):
        ...

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
    def untargz_cached_file               (self, tarGzFilePath, extractTargetPath):
    def install_linux_game_server         (self, choosen_version=None):
    def update_ini_file_value             (self, server_localname, ini_filename, key_to_update, new_value):
    
    -- mod.io
    def install_mod                       (self, mod_url_to_download):

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
        import os
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
        import psutil
        import os
        from sys import platform
        from subprocess import check_output
        from subprocess import CalledProcessError   

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
                if "\Win64\MCSServer.exe" in line:
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
                            "server_gamename"  : splitted_line[4].split("=")[1]
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
        import os
        os.symlink(
            os.path.abspath(symlink_source_path), 
            os.path.abspath(symlink_target_path)
        )
        return True


    ##########
    # GET INFORMATIONS
    def get_server_list_full_Path(self, directory_path):
        import os

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
        import os
        import re

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
        import os
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
        import os
        import re

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
        import subprocess
        import re
        import os
        from sys import platform

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
            import time
            time.sleep(6)
        

        print(f"    ->  Server {server_localname} has been started")
        return server.pid

    def start_server_by_id(self, server_port):
        server_localname = self.find_server_localname_by_id(server_port)

        if server_localname is not None:
            if not self.is_server_already_started(server_localname):
                server_pid = self.start_server_by_localname(server_localname)
                print(f"    ->  Server {server_localname} started with pid {server_pid}")
            else:
                print(f"    ->  Server {server_localname} already started.")
        else:
            print(f"    ->  No server found with id {server_port}")


    ##########
    # STOP SERVER 
    def kill_server_by_localname(self, server_localname):
        import os
        import psutil
        import signal
        import subprocess
        import time
        from subprocess import check_output

        server_is_active = self.is_server_already_started(server_localname)
        if not server_is_active:
            print(f"    -> Server {server_localname} is not currently active.")
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
            print("Warning : No server found, no shutdown")
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
            print("Info : No server found on second SIGINT, seems server has been killed on first SIGINT")

        # Check that server is shutdown (don't use psutil because I want to check the path)
        try:
            serverDed = True
            all_started_servers = self.get_all_started_servers()
            if all_started_servers:
                for server in all_started_servers:
                    if server_localname in server['server_localname']:
                        print("Warning : Server still alive")
                        serverDed = False
            if serverDed:
                print(f"    -> Server {server_localname} has been shutdown")
        except subprocess.CalledProcessError as e:
            print(f"    ->  Server {server_localname} has been shutdown")

    def kill_server_by_id(self, server_port):
        server_localname = self.find_server_localname_by_id(server_port)

        if server_localname is not None:
            print(f"Killing server {server_localname}...")
            server_pid = self.kill_server_by_localname(server_localname)
        else:
            print(f"No server found with id {server_port}")

    # RESTART
    def restart_server_by_localname(self, server_localname):
        import time
        import psutil
        import os
        from subprocess import check_output

        pidlist = check_output(["pidof", "MCSServer"], universal_newlines=True).split()
        serverList = self.get_server_list_only_localname(os.getcwd())
        print(pidlist)
        if serverList is not None:
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_localname in p.exe():
                    liveServerArgs = p.cmdline()
                    for arg in liveServerArgs:
                        if "-port=" in arg:
                            self.DATA['gameServer_port'] = arg.split("=")[1]
                        if "game=" in arg:
                            self.DATA['gameServerMode'] = arg.split("=")[1]
                        if "?" in arg:
                            self.DATA['gameServerMap'] = arg.split("?")[0]
                        if "-servername=" in arg:
                            self.DATA['gameServer_gamename'] = arg.split("=")[1]

                    self.kill_server_by_localname(server_localname)
                    time.sleep(1)
                    self.start_server_by_localname(server_localname)
        else:
            print("No server installed.")


    def restart_server_by_id(self, server_port):
        self.restart_server_by_localname(self.find_server_localname_by_id(server_port))




    '''


    Global functions


    '''

    def create_server_folder_structure(self, server_init_path=None):
        import os

        if server_init_path is None:
            server_init_path = os.getcwd()

        print("Check that path has not been initialized already.")
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
                    print(f"    Creating - {ftc}")
                    os.makedirs(ftc)
                else:
                    print(f"    Already exists - {ftc}")

            print("    ->  Current directory has been init for vertex servers.")
        else:
            print("    ->  Seems directory has already been initialized")
            print("    ->  Please check for existence for the fallowing folders")
            print("            ./maps/")
            print("            ./servers/")
            print("            ./cache/")
            print("            ./donotdelete/")
            print("            ./donotdelete/maps/ (which content equals ./maps/)")
            print("            ./vsm/")
            print("    ->  If init has failed, please remove all folders but ./vsm/")
            print("    ->  Init will stop")


    def download_file_to_cache(self, url_to_download):
        from urllib.request import urlopen
        filename = url_to_download.split("/")[-1:][0]
        cache_file_path = f"cache/{filename}"
        # Download from URL
        with urlopen(url_to_download) as file:
            content = file.read()
        # Save to file
        with open(cache_file_path, 'wb') as download:
            download.write(content)
        return cache_file_path


    def untargz_cached_file(self, tarGzFilePath, extractTargetPath):
        import tarfile
        fileExtractor = tarfile.open(tarGzFilePath)
        fileExtractor.extractall(extractTargetPath)
        fileExtractor.close()

        
    def unzip_cached_file(self, zipFilePath, extractTargetPath):
        import zipfile
        with zipfile.ZipFile(zipFilePath, 'r') as zip_ref:
            zip_ref.extractall(extractTargetPath)


    def install_game_server(self, choosen_version=None):
        import copy
        import os
        import psutil
        import shutil
        import stat
        import subprocess
        import time
        from sys import platform

        global DATA
        
        if platform == "linux" or platform == "linux2":
            ...
        elif platform == "darwin":
            print("OSX not supported right now currently")
        elif platform == "win32":
            ...


        if choosen_version is None:
            import requests
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
            print("Warning : Folder has not been init, script will stop.")
            print("You can init the folder doing like : python ./vsm.py --init")
            return

        print("Downloading server archive to ./cache/ ...")
        downloaded_file_path = self.download_file_to_cache(url_to_download)
        print("    ->  Done")

        print("Extracting server archive file into ./cache/")
        
        if platform == "linux" or platform == "linux2":
            self.untargz_cached_file(downloaded_file_path, './cache')
        elif platform == "win32":
            self.unzip_cached_file(downloaded_file_path, './cache')
        
        print("    ->  Done")

        print("Deleting downloaded file from ./cache/")
        os.remove(downloaded_file_path)
        print("    ->  Done")
        

        ############################################################
        # Define new server identity
        new_server_number = self.get_current_highest_gameserver_id()
        if new_server_number is None:
            new_server_number = self.DATA['defaultStartingPort']
        else:
            new_server_number += 1
        new_server_localname = copy.copy(self.DATA['server_localnameTemplate']).replace("<NUMBER>", str(new_server_number))
        print(f"New server name will be : {new_server_localname}")
        
        # Move files
        print("Move server file to ./servers/")
        
        if platform == "linux" or platform == "linux2":
            server_source = "./cache/launcher/files/mcs_server_linux/Server"
        elif platform == "win32":
            server_source = "./cache/Server"
        
        server_destination = f"./servers/{new_server_localname}"
        shutil.move(server_source, server_destination)
        print("    ->  Done")


        ############################################################
        # Remove useless files from cache
        
        if platform == "linux" or platform == "linux2":
            print("Clean ./cache/ from useless files")
            shutil.rmtree('./cache/launcher/')
            print("    ->  Done")

        
        ############################################################
        # Make server binary executable
        if platform == "linux" or platform == "linux2":
            linux_binary = f"./servers/{new_server_localname}/MCS/Binaries/Linux/MCSServer"
            st = os.stat(linux_binary)
            os.chmod(linux_binary, st.st_mode | stat.S_IEXEC)


        ############################################################
        # Start server
        print("Make first server start to generate conf files etc.")
        server_pid = self.start_server_by_localname(new_server_localname)

        if psutil.pid_exists(server_pid):
            print("    ->  Server has started correctly")

        # Wait for init to end
        print("Waiting 6 seconds to let server do his init")
        time.sleep(6)
        print("    ->  Done")

        # Checking that server is alive as expected
        if not psutil.pid_exists(server_pid):
            print("!!!!! Server is not alive, something might be wrong !!!!!")


        ############################################################
        # Kill the server nicely to force save of config files

        print("Shutting down the server properly")
        self.kill_server_by_localname(new_server_localname)


        ############################################################
        # Make symlink to add map folder to gameserver to optimize spacedisk
        print("Make symlink of ./maps/ inside UserCreatedContent")
        # That is the part that requires having Admin rights
        symlink_has_been_created = self.create_symlink("./maps/", f"./servers/{new_server_localname}/MCS/UserCreatedContent/maps/")
        if symlink_has_been_created:
            print("    ->  Done")
        else:
            print("    ->  Error")
        print("\n----------\n")
        print(f"Server installation has finished for {new_server_localname}.")
        print("\n----------\n")

    def update_ini_file_value(self, server_localname, ini_filename, key_to_update, new_value):
        import configparser
        import os
        import ast
        
        ini_file_path = "./servers/<SERVER_LOCALNAME>/MCS/Saved/Config/LinuxServer/<INI_FILENAME>"
        ini_file_path = ini_file_path.replace("<SERVER_LOCALNAME>", server_localname)
        ini_file_path = ini_file_path.replace("<INI_FILENAME>", ini_filename)

        if not os.path.exists(ini_file_path):
            print(f"File '{ini_file_path}' not found.")
            return False

        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read(ini_file_path)

        key_has_been_found = False
        for section in config_parser.sections():
            section_dict = dict(config_parser.items(section))
            for key in section_dict:
                if key == key_to_update:
                    key_has_been_found = True
                    original_value = section_dict[key]
                    eval_ini_value = None
                    eval_new_value = None

                    try:
                        eval_ini_value = ast.literal_eval(section_dict[key])
                    except:
                        eval_ini_value = section_dict[key]

                    try:
                        eval_new_value = ast.literal_eval(new_value)
                    except:
                        eval_new_value = new_value

                    type_of_ini_value = type(eval_ini_value)
                    type_of_new_value = type(eval_new_value)

                    if type_of_new_value is type_of_ini_value:
                        config_parser.set(section, key_to_update, new_value)
                        with open(ini_file_path, 'w') as configfile:
                            config_parser.write(configfile, space_around_delimiters=False)
                            print(f"Config key '{key_to_update}' of '{ini_file_path}' has been updated from '{original_value}' to '{new_value}'.")
                        break
                    else:
                        print(f"Value mismatch : ini value is type '{type_of_ini_value}' and new value is type '{type_of_new_value}'.")
                        break

        if not key_has_been_found:
            print(f"Config key '{key_to_update}' has not been found inside '{ini_file_path}'.")
        return key_has_been_found


    '''


    mod.io


    '''


    def install_mod(self, mod_url_to_download):
        import os
        import shutil
        import zipfile
        from urllib.request import urlopen

        if not self.is_folder_has_been_initialized(os.getcwd()):
            print("Warning : Folder has not been init, script will stop.")
            print("You can init the folder doing like : python ./vsm.py --init")
            return

        print("Checking URL...")
        invalid_provided_url_error_message = "Error : Invalid URL : please provide a url like https://api.mod.io/v1/games/594/mods/<mod_id>/files/<file_id>/download"
        split_url = mod_url_to_download.split("/")
        '''
        ['https:', '', 'api.mod.io', 'v1', 'games', <gameid>, 'mods', <modid>, 'files', <fileid>, 'download']
        '''
        if(len(split_url) != 11):
            print(invalid_provided_url_error_message)
            return False

        if (
            split_url[2] != 'api.mod.io' and
            split_url[4] != 'games'      and
            split_url[5] != '594'        and
            split_url[6] != 'mods'       and
            split_url[8] != 'files'
        ):
            print(invalid_provided_url_error_message)
            return False

        print(f"    Checking URL '{mod_url_to_download}' ...")
        # real_mod_url = urlopen(mod_url_to_download).geturl()
        
        import requests

        url = requests.get(mod_url_to_download)
        htmltext = url.text
        print(htmltext)

        real_mod_url = "https://binary.modcdn.io/mods/c9d5/1049908/kyleball-client.zip?verify=1713904215-2Ng7SEzuKyyYXukbzV83RBT5m9oVC2E3ADFyix5p8DI%3D"
        print(f"    Found real file location as '{real_mod_url}'")

        if(urlopen(real_mod_url).getheader('Content-Type') != "application/zip"):
            print("Error : File type is not zip.")
            return False
        print("    ->  Done")
        mod_id               = split_url[7]
        server_init_path     = os.getcwd()
        new_mod_cache_path   = f"{server_init_path}/cache/{mod_id}"
        new_mod_maps_path    = f"{server_init_path}/maps/{mod_id}"
        filename_to_download = real_mod_url.split("/")[-1]
        check_file_exists    = f"{server_init_path}/cache/{filename_to_download}"

        if os.path.isfile(check_file_exists):
            print(f"Warning : Doing cleanup, removes pre-existing '{check_file_exists}'.")
            os.remove(check_file_exists)
            print(f"    ->  Done")

        # Download
        print(f"Downloading '{real_mod_url}'...")
        cache_downloaded_mod_zip = self.download_file_to_cache(real_mod_url)
        print(f"    ->  Done")

        # Clean leftovers of a previous attempt and create
        if os.path.isdir(new_mod_cache_path):
            print(f"Warning : Doing cleanup, removes pre-existing '{new_mod_cache_path}'.")
            shutil.rmtree(new_mod_cache_path)
            print(f"    ->  Done")
        print(f"Creating '{new_mod_cache_path}'...")
        os.makedirs(new_mod_cache_path)
        print(f"    ->  Done")

        # Unzip to new folder
        print(f"Extracting '{cache_downloaded_mod_zip}'...")
        with zipfile.ZipFile(cache_downloaded_mod_zip, 'r') as zip_ref:
            zip_ref.extractall(new_mod_cache_path)
        print(f"    ->  Done")

        # Remove existing mod in ./maps/ and place new folder inside it
        if os.path.isdir(new_mod_maps_path):
            print(f"Warning : Doing cleanup, removes pre-existing '{new_mod_maps_path}'.")
            shutil.rmtree(new_mod_maps_path)
            print(f"    ->  Done")
        print(f"Moving '{new_mod_cache_path}' to '{new_mod_maps_path}'...")
        shutil.move(new_mod_cache_path, new_mod_maps_path)
        print(f"    ->  Done")
        print(f"Removing '{cache_downloaded_mod_zip}'...")
        os.remove(cache_downloaded_mod_zip)
        print(f"    ->  Done")
        
        print(f"Success : Mod id {mod_id} with filename {filename_to_download} successfully downloaded and installed.")
        return True

