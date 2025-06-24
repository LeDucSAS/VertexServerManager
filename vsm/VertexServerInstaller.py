import copy
import logging
import psutil
import os
import requests
import re
import stat
import time
from vsm.VertexServerDownloader import VertexServerDownloader
from vsm.VertexServerManager import VertexServerManager
from vsm.VsmFileManager import VsmFileManager
from vsm.VsmData import VsmData
from sys import platform


logger = logging.getLogger("VertexServerInstaller")


class VertexServerInstaller():
    def __init__(self):
        self.vfm = VsmFileManager()
        self.vsm = VertexServerManager()
        self.vsd = VertexServerDownloader()
        self.DATA = VsmData().DATA


    def create_server_folder_structure(self, server_init_path=None):
        logger.debug("create_server_folder_structure() ...")
        if server_init_path is None:
            server_init_path = os.getcwd()

        logger.info("Check that path has not been initialized already.")
        if not self.vsm.is_folder_has_been_initialized():
            logger.debug("Folder has not been initialized")
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
            logger.debug("Folder was already initialized")
            logger.info("    ->  Seems directory has already been initialized")
            logger.info("    ->  Please check for existence for the fallowing folders")
            logger.info("            ./maps/")
            logger.info("            ./servers/")
            logger.info("            ./cache/")
            logger.info("            ./vsm/")
            logger.info("    ->  If init has failed, please remove all folders but ./vsm/")
            logger.info("    ->  Init will stop")
        logger.debug("create_server_folder_structure() done")


    def install_game_server(self, choosen_version=None):
        logger.debug("install_game_server() ...")
        logger.debug(f"Param choosen_version is {choosen_version}")
        global DATA
        
        logger.debug(f"Platform is {platform}")
        if platform == "linux" or platform == "linux2":
            ...
        elif platform == "darwin":
            logger.info("OSX not supported right now currently")
        elif platform == "win32":
            ...

        if choosen_version is None:
            response = requests.get(self.DATA['apiVersion'])
            choosen_version = response.json()['version']
        
        logger.debug(f"Preparing url_to_download for platform {platform}")
        if platform == "linux" or platform == "linux2":
            url_to_download = copy.copy(self.DATA['fileVertexServerFullLinux']).replace("<VERSION>", choosen_version)
        elif platform == "win32":
            url_to_download = copy.copy(self.DATA['fileVertexServerFullWindows']).replace("<VERSION>", choosen_version)
        

        ############################################################
        # Check init, download, unzip, clean cache
        folder_has_been_init = self.vsm.is_folder_has_been_initialized(os.getcwd())
        if not folder_has_been_init:
            logger.info("Warning : Folder has not been init, script will stop.")
            logger.info("You can init the folder doing like : python ./vsm.py --init")
            return

        logger.info("Downloading server archive to ./cache/ ...")
        downloaded_file_path = self.vsd.download_file_to_cache(url_to_download)
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
        new_server_number = self.vsm.get_current_highest_gameserver_id()
        if new_server_number is None:
            new_server_number = self.DATA['defaultStartingPort']
        else:
            new_server_number += 1
        logger.info(f"New server ID will be : {new_server_number}")
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
        server_pid = self.vsm.start_server_by_localname(new_server_localname)

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
        self.vsm.kill_server_by_localname(new_server_localname)


        ############################################################
        # Make symlink to add map folder to gameserver to optimize spacedisk
        logger.info("Make symlink of ./maps/ inside UserCreatedContent")
        # That is the part that requires having Admin rights
        symlink_has_been_created = self.vfm.create_symlink("./maps/", f"./servers/{new_server_localname}/MCS/UserCreatedContent/maps/")
        if symlink_has_been_created:
            logger.info("    ->  Done")
        else:
            logger.info("    ->  Error")
        logger.info(f"Server installation has finished for {new_server_localname}.")
        logger.debug("install_game_server() done")

