# LeDucSAS - Vertex Server Manager (VSM)
# License : Free art license 1.3 https://artlibre.org/

class VertexServerManager():
    def __init__(self):
        ...

    """

    Class Structure
    Data
    def __init__(self):
    def is_folder_has_been_initialized    (self, directory_path=None):
    def is_server_already_started         (self, server_name):
    def create_symlink                    (self, symlink_source_path, symlink_target_path):
    def get_server_list_full_Path         (self, directory_path):
    def get_server_list_only_name         (self, directory_path=None):
    def find_server_name_by_id            (self, server_port):
    def get_current_highest_gameserver_id (self, directory_path=None):
    def start_server_by_name              (self, server_name):
    def start_server_by_id                (self, server_port):
    def kill_server_by_name               (self, server_name):
    def kill_server_by_id                 (self, server_port):
    def restart_server_by_name            (self, server_name):
    def restart_server_by_id              (self, server_port):
    def create_server_folder_structure    (self, server_init_path=None):
    def download_file_to_cache            (self, url_to_download):
    def untargz_cached_file               (self, tarGzFilePath, extractTargetPath):
    def install_linux_game_server         (self, choosen_version=None):
    def update_ini_file_value             (self, server_name, ini_filename, key_to_update, new_value):
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

    DATA['server_nameTemplate'] = "GameServer<NUMBER>"
    DATA['defaultStartingPort'] = 27070

    DATA['gameServerMap']       = "P_FFA_COMPLEX"
    DATA['gameServerMode']      = "OPEN"
    DATA['gameServer_port']     = -1
    DATA['gameServer_name']     = "You forgot to setup my server name"




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

    def is_server_already_started(self, server_name):
        import psutil
        import subprocess
        from subprocess import check_output
        try:
            serverDed = True
            pidlist = check_output(["pidof","MCSServer"], universal_newlines=True).split()
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_name in p.exe():
                    return True
            if serverDed:
                return False
        except subprocess.CalledProcessError as e:
            return False

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

    def get_server_list_only_name(self, directory_path=None):
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

    def find_server_name_by_id(self, server_port):
        import os
        directory_path = os.getcwd()
        serverList = self.get_server_list_only_name(directory_path)
        has_server_name_been_found = False
        if serverList is not None:
            for server_name in serverList:
                if server_name.endswith(str(server_port)):
                    has_server_name_been_found = True
                    return server_name
        if not has_server_name_been_found:
            return None


    def get_current_highest_gameserver_id(self, directory_path=None):
        import os
        import re

        if directory_path == None:
            directory_path = os.getcwd()

        gameServerList = self.get_server_list_full_Path(directory_path)
        if gameServerList is not None:
            tmp = []
            for server in gameServerList:
                tmp.append(int(re.sub('[^0-9]','', server)))
            tmp.sort()
            return int(tmp[-1])
        else:
            return None


    ##########
    # START SERVER
    def start_server_by_name(self, server_name):
        import subprocess
        import re

        if int(self.DATA['gameServer_port']) < 1:
            self.DATA['gameServer_port'] = re.sub('[^0-9]','', server_name)
        
        server = subprocess.Popen([
                f"./servers/{server_name}/MCS/Binaries/Linux/MCSServer {self.DATA['gameServerMap']}?game={self.DATA['gameServerMode']} -port={self.DATA['gameServer_port']} -server_name='{self.DATA['gameServer_name']}'"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
        print(f"    ->  Server {server_name} has been started")
        return server.pid

    def start_server_by_id(self, server_port):
        server_name = self.find_server_name_by_id(server_port)

        if server_name is not None:
            if not self.is_server_already_started(server_name):
                server_pid = self.start_server_by_name(server_name)
                print(f"    ->  Server {server_name} started with pid {server_pid}")
            else:
                print(f"    ->  Server {server_name} already started.")
        else:
            print(f"    ->  No server found with id {server_port}")


    ##########
    # STOP SERVER 
    def kill_server_by_name(self, server_name):
        import os
        import psutil
        import signal
        import subprocess
        import time
        from subprocess import check_output

        errorNoServer = False
        # First SIGINT
        try:
            pidlist = check_output(["pidof","MCSServer"], universal_newlines=True).split()
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_name in p.exe():
                    os.kill(int(pid), signal.SIGINT)
        except subprocess.CalledProcessError as e:
            errorNoServer = True

        if errorNoServer:
            print("Warning : No server found, no shutdown")
            return

        # Wait for shutdown before the second SIGINT
        time.sleep(6)

        # Second SIGINT (as required)
        try:
            pidlist = check_output(["pidof","MCSServer"], universal_newlines=True).split()
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_name in p.exe():
                    os.kill(int(pid), signal.SIGINT)
        except subprocess.CalledProcessError as e:
            print("Info : No server found on second SIGINT, seems server has been killed on first SIGINT")

        # Check that server is shtudown (don't use psutil because I want to check the path)
        try:
            serverDed = True
            pidlist = check_output(["pidof","MCSServer"], universal_newlines=True).split()
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_name in p.exe():
                    print("Warning : Server still alive")
                    serverDed = True
            if serverDed:
                print(f"    ->  Server {server_name} has been shutdown")
        except subprocess.CalledProcessError as e:
            print(f"    ->  Server {server_name} has been shutdown")

    def kill_server_by_id(self, server_port):
        server_name = self.find_server_name_by_id(server_port)

        if server_name is not None:
            print(f"Killing server {server_name}...")
            server_pid = self.kill_server_by_name(server_name)
        else:
            print(f"No server found with id {server_port}")

    # RESTART
    def restart_server_by_name(self, server_name):
        import time
        import psutil
        from subprocess import check_output

        pidlist = check_output(["pidof", "MCSServer"], universal_newlines=True).split()
        if serverList is not None:
            for pid in pidlist:
                p = psutil.Process(int(pid))
                if server_name in p.exe():
                    liveServerArgs = p.cmdline()
                    for arg in liveServerArgs:
                        if "-port=" in arg:
                            self.DATA['gameServer_port'] = arg.split("=")[1]
                        if "game=" in arg:
                            self.DATA['gameServerMode'] = arg.split("=")[1]
                        if "?" in arg:
                            self.DATA['gameServerMap'] = arg.split("?")[0]
                        if "-server_name=" in arg:
                            self.DATA['gameServer_name'] = arg.split("=")[1]

                    self.kill_server_by_name(server_name)
                    time.sleep(1)
                    self.start_server_by_name(server_name)
        else:
            print("No server installed.")


    def restart_server_by_id(self, server_port):
        self.restart_server_by_name(self.find_server_name_by_id(server_port))




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

            os.makedirs(map_folder_path)
            os.makedirs(server_folder_path)
            os.makedirs(cache_folder_path)

            print("    ->  Current directory has been init for vertex servers")
        else:    
            print("    ->  Init require an empty directory (except server-manager script)")
            print("    ->  Current directory is not empty")
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


    def install_linux_game_server(self, choosen_version=None):
        import copy
        import os
        import psutil
        import shutil
        import stat
        import subprocess
        import time

        global DATA

        if choosen_version is None:
            import requests
            response = requests.get(self.DATA['apiVersion'])
            choosen_version = response.json()['version']

        url_to_download = copy.copy(self.DATA['fileVertexServerFullLinux']).replace("<VERSION>", choosen_version)


        ############################################################
        # Check init, download, unzip, clean cache
        folder_has_been_init = self.is_folder_has_been_initialized(os.getcwd())
        if not folder_has_been_init:
            print("Warning : Folder has not been init, script will stop.")
            return

        print("Downloading server archive to ./cache/ ...")
        downloaded_file_path = self.download_file_to_cache(url_to_download)
        print("    ->  Done")

        print("Extracting server archive file into ./cache/")
        self.untargz_cached_file(downloaded_file_path, './cache')
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
        new_server_name = copy.copy(self.DATA['server_nameTemplate']).replace("<NUMBER>", str(new_server_number))
        # Move files
        print("Move server file to ./servers/")
        server_source = "./cache/launcher/files/mcs_server_linux/Server"
        server_destination = f"./servers/{new_server_name}"
        shutil.move(server_source, server_destination)
        print("    ->  Done")


        ############################################################
        # Remove useless files from cache
        print("Clean ./cache/ from useless files")
        shutil.rmtree('./cache/launcher/')
        print("    ->  Done")
        

        ############################################################
        # Make server binary executable
        linux_binary = f"./servers/{new_server_name}/MCS/Binaries/Linux/MCSServer"
        st = os.stat(linux_binary)
        os.chmod(linux_binary, st.st_mode | stat.S_IEXEC)


        ############################################################
        # Start server
        print("Make first server start to generate conf files etc.")
        server_pid = self.start_server_by_name(new_server_name)

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
        self.kill_server_by_name(new_server_name)


        ############################################################
        # Make symlink to add map folder to gameserver to optimize spacedisk
        print("Make symlink of ./maps/ inside UserCreatedContent")

        symlink_has_been_created = self.create_symlink("./maps/", f"./servers/{new_server_name}/MCS/UserCreatedContent/maps/")
        if symlink_has_been_created:
            print("    ->  Done")
        else:
            print("    ->  Error")


    def update_ini_file_value(self, server_name, ini_filename, key_to_update, new_value):
        import configparser
        import os
        import ast
        
        ini_file_path = "./servers/<SERVER_NAME>/MCS/Saved/Config/LinuxServer/<INI_FILENAME>"
        ini_file_path = ini_file_path.replace("<SERVER_NAME>", server_name)
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


    def install_mod(self, mod_url_to_download):
        import os
        import shutil
        import zipfile
        from urllib.request import urlopen

        if not self.is_folder_has_been_initialized(os.getcwd()):
            print("Warning : Folder has not been init, script will stop.")
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

        real_mod_url = urlopen(mod_url_to_download).geturl()

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




'''


ARGPARSE AREA


'''

# Argparse data structure
'''
{
    'init'                 : False, # Boolean automatic set
    'install_server'       : False, # Boolean automatic set
    'start_id'             : None,  # int
    'kill_id'              : None,  # int
    'restart_id'           : None,  # int
    'kill_all'             : False, # Boolean automatic set
    'restart_all'          : False, # Boolean automatic set
    'set_server_name'      : None,  # str
    'set_server_port'      : None,  # int
    'set_server_map'       : None,  # str
    'set_server_mode'      : None,  # str
    'ini_update_server_id' : None,  # int
    'ini_file'             : None,  # str
    'ini_update_key'       : None,  # str
    'ini_new_value'        : None,  # str
    'install_mod'          : None   # str (URL)
}
'''


import argparse
import sys

parser = argparse.ArgumentParser( description="LeDucSAS - Vertex Server Manager", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Setup and installation
parser.add_argument("--init"          , action="store_true", help="Initialize the folder by creating ./cache/, ./servers/ and ./maps/ folder.")
parser.add_argument("--install-server", action="store_true", help="Download and install a new server")
# parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")

# Server start, stop, restart
parser.add_argument('-s', '--start-id'  , nargs='?', const=-1, type=int, help="Start server by port")
parser.add_argument('-k', '--kill-id'   , nargs='?', const=-1, type=int, help="Restart server by port")
parser.add_argument('-r', '--restart-id', nargs='?', const=-1, type=int, help="Restart server by port")

# parser.add_argument('--start-all', action="store_true", help="Start server by port")
parser.add_argument('--kill-all'   , action="store_true", help="Restart server by port")
parser.add_argument('--restart-all', action="store_true", help="Restart server by port")

# Server configuration
parser.add_argument('--set-server-name', nargs='?', const=None, type=str, help="Force non default game server name")
parser.add_argument('--set-server-port', nargs='?', const=None, type=int, help="Force non default game server port")
parser.add_argument('--set-server-map' , nargs='?', const=None, type=str, help="Force non default game server map")
parser.add_argument('--set-server-mode', nargs='?', const=None, type=str, help="Force non default game server gamemode")

# .INI file updates
parser.add_argument('--ini-update-server-id', nargs='?'          , const=None, type=int, help="Select the server to be updated")
parser.add_argument('--ini-file'            , nargs='?'          , const=None, type=str, help="Select the file to be updated")
parser.add_argument('--ini-update-key'      , nargs='?'          , const=None, type=str, help="Select the key to be updated")
parser.add_argument('--ini-new-value'       , nargs='?'          , const=None, type=str, help="Define the new value")

# Mod installation from mod.io
parser.add_argument('--install-mod', nargs='?', const=None, type=str, help="Input URL of mod.io file to download")


# Save and make parser
args = parser.parse_args()
config = vars(args)

# Display help by default if no argument is given
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)




'''


Command line arguments interpretation


'''

vsm = VertexServerManager()


# Server parameter
if config["set_server_name"]:
    vsm.DATA['gameServer_name'] = config["set_server_name"]

if config["set_server_port"] is not None:
    if config["set_server_port"] > 0:
        vsm.DATA['gameServer_port'] = config["set_server_port"]

if config["set_server_map"]:
    vsm.DATA['gameServerMap'] = config["set_server_map"]

if config["set_server_mode"]:
    vsm.DATA['gameServerMode'] = config["set_server_mode"]


# Do init
if config["init"] == True:
    vsm.create_server_folder_structure()


# Do server install
if config["install_server"] == True:
    from sys import platform
    if platform == "linux" or platform == "linux2":
        vsm.install_linux_game_server()
    elif platform == "darwin":
        print("OSX not supported right now currently")
    elif platform == "win32":
        print("Windows not supported right now currently")


# Do start server by port number
if config["start_id"]:
    if config["start_id"] > 0:
        vsm.start_server_by_id(config["start_id"])
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Do kill server by port number
if config["kill_id"]:
    if config["kill_id"] > 0:
        vsm.kill_server_by_id(config["kill_id"])
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Do restart server by port number
if config["restart_id"]:
    displayServers = False
    if config["restart_id"] > 0:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            displayNoIdFound = True
            for server_name in serverList: 
                if server_name.endswith(str(config["restart_id"])):
                    print(f"Will restart {server_name}")
                    vsm.restart_server_by_name(server_name)
                    displayNoIdFound = False
                    break
            if displayNoIdFound:
                print(f'No server found with id {config["restart_id"]}')
                displayServers = True
        else:
            print("No server started.")
            displayServers = True
    else:
        displayServers = True

    if displayServers:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")

''' Desactivated because can't properly specify values unless relying on creating a config file'''
# Do start all server
# if config["start_all"]:
#   import os
#   serverList = vsm.get_server_list_only_name(os.getcwd())
#   if serverList is not None:
#       print("Will start all servers")
#       for server_name in serverList: vsm.start_server_by_name(server_name)
#   else:
#       print("No server installed.")


# Do kill all server
if config["kill_all"]:
    import os
    serverList = vsm.get_server_list_only_name(os.getcwd())
    if serverList is not None:
        print("Will kill all servers")
        for server_name in serverList: 
            vsm.kill_server_by_name(server_name)
    else:
        print("No server installed.")


# Do restart all server
if config["restart_all"]:
    import os
    serverList = vsm.get_server_list_only_name(os.getcwd())
    if serverList is not None:
        print("Will restart all servers")
        for server_name in serverList: 
            vsm.restart_server_by_name(server_name)
    else:
        print("No server installed.")


# Update ini file
if config["ini_update_server_id"]:
    # check server exists
    if config["ini_update_server_id"] > 0:
        server_name = vsm.find_server_name_by_id(config["ini_update_server_id"])
        if not vsm.is_server_already_started(server_name):
            if server_name is not None:
                if (
                    config['ini_file']       is not None and 
                    config['ini_update_key'] is not None and
                    config['ini_new_value']  is not None
                ):
                    vsm.update_ini_file_value(server_name, config['ini_file'], config['ini_update_key'], config['ini_new_value'])
                else:
                    print("Error : Script require the 4 arguments : --ini-update-server-id, --ini-file, --ini-update-key, --ini-new-value.")
            else:
                print(f"Can't find a server with id : {config['ini_update_server_id']}")
        else:
            print(f"Server {server_name} is already started. No .ini update will be done.")
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Install new modfile
if config["install_mod"]:
    vsm.install_mod(config["install_mod"])
