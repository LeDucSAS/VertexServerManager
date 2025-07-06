import logging
import os
from vsm.VsmDownloader import VsmDownloader
from vsm.VsmFileManager import VsmFileManager


logger = logging.getLogger("ModioDownloadManager")


class ModioDownloadManager():

    def __init__(self, yaml_data):
        self.enable_cache_purification = True
        self.MIODM = {}
        # Technical data to access the mod file
        self.MIODM["game_id"] = yaml_data["game_id"]
        self.MIODM["mod_id"] = ''
        self.MIODM["file_id"] = ''
        self.MIODM["api_key"] = yaml_data["api_key"]
        # Technical data about the file
        self.MIODM["archive_url"] = ''
        # Local data
        self.MIODM["downloaded_file_path"] = ''
        self.MIODM["extracted_file_path"] = ''
        self.vfm = VsmFileManager()
    

    def mod_list(self):
        # list all, list available, list installed
        ...


    def mod_install_direct_url(self, direct_mod_file_url_to_download:str):
        logger.debug("mod_install_direct_url() ...")
        try:
            game_id = direct_mod_file_url_to_download.split("/games/")[1].split("/")[0]
            if not (int(self.MIODM["game_id"]) == int(game_id)):
                return False
            self.MIODM["mod_id"] = direct_mod_file_url_to_download.split("/mods/")[1].split("/")[0]
            self.MIODM["file_id"] = direct_mod_file_url_to_download.split("/files/")[1].split("/")[0]
            self.MIODM["archive_url"] = f"https://api.mod.io/v1/games/{self.MIODM['game_id']}/mods/{self.MIODM['mod_id']}/files/{self.MIODM['file_id']}/download?api_key={self.MIODM['api_key']}"
        except:
            logger.critical("An exception occurred")
            return False

        if(self.enable_cache_purification):
            self.vfm.cache_purification() # Removes everything but .gitignore
        downloaded_file = VsmDownloader().download_to_cache(self.MIODM["archive_url"])
        downloaded_file_path = f"cache/{downloaded_file}"
        self.file_extract_to_cache(downloaded_file_path, self.MIODM["mod_id"])
        self.file_move_from_cache_and_overwrite_to_maps(self.MIODM["mod_id"])
        self.vfm.cache_mod_cleanup(f"{os.getcwd()}/cache/{self.MIODM["mod_id"]}/", f"{os.getcwd()}/{downloaded_file_path}")
        
        logger.debug("mod_install_direct_url() => done")


    def file_extract_to_cache(self, file_path:str, mod_id:str):
        logger.debug("file_extract_to_cache() ...")
        # Create a folder with the ID of the mod so it easier to update
        self.MIODM["extracted_file_path"] = f'{os.getcwd()}/cache/{mod_id}'
        target_path = self.MIODM["extracted_file_path"]
        os.mkdir(target_path)
        file_ext = file_path.split("/")[-1].split(".")[1]
        if file_ext == "zip":
            self.vfm.unzip_file(file_path, target_path)
        logger.debug("file_extract_to_cache() => done")


    def file_move_from_cache_and_overwrite_to_maps(self, mod_id:str):
        logger.debug("file_move_from_cache_and_overwrite_to_maps() ...")
        source = f"{os.getcwd()}/cache/{mod_id}"
        destination = f"{os.getcwd()}/maps/{mod_id}"
        if os.path.isdir(destination):
            logger.info(f"Deleting pre-existing '{destination}'.")
            self.vfm.remove_at_path(destination)
        logger.info(f"Moving mod folder from cache to maps folder'.")
        self.vfm.move_folder(source, destination)
        if os.path.isdir(destination):
            logger.info(f"Move success '{destination}'.")
        logger.debug("file_move_from_cache_and_overwrite_to_maps() => done")

