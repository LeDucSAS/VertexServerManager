import logging
import os
import re
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
    

    def mod_list(self) -> None:
        # list all, list available, list installed
        ...


    def mod_install_direct_url(self, direct_mod_file_url_to_download: str) -> bool:
        logger.debug("mod_install_direct_url() ...")
        
        match = re.search(r'/games/(\d+)/mods/(\d+)/files/(\d+)', direct_mod_file_url_to_download)
        if not match:
            logger.error(f"URL is invalid or with wrong format : {direct_mod_file_url_to_download}")
            return False

        game_id, mod_id, file_id = match.groups()

        if int(self.MIODM["game_id"]) != int(game_id):
            logger.error(f"Game ID mismatch: expected {self.MIODM['game_id']}, got {game_id}")
            return False

        self.MIODM["mod_id"] = mod_id
        self.MIODM["file_id"] = file_id
        self.MIODM["archive_url"] = f"https://api.mod.io/v1/games/{game_id}/mods/{mod_id}/files/{file_id}/download?api_key={self.MIODM['api_key']}"

        if self.enable_cache_purification:
            VsmFileManager.clear_cache()

        try:
            downloaded_file = VsmDownloader().download_to_cache(self.MIODM["archive_url"])
            downloaded_file_path = f"cache/{downloaded_file}"
        except Exception as e:
            logger.exception("Failure download to cache.")
            return False

        self.file_extract_to_cache(downloaded_file_path, mod_id, file_id)
        self.file_move_from_cache_and_overwrite_to_maps(mod_id, file_id)
        
        VsmFileManager.cache_mod_cleanup(f"{os.getcwd()}/cache/{mod_id}/", f"{os.getcwd()}/{downloaded_file_path}")
        
        logger.debug("mod_install_direct_url() => done")
        return True


    def file_extract_to_cache(self, file_path:str, mod_id:str, file_id:str) -> None:
        logger.debug("file_extract_to_cache() ...")
        
        self.MIODM["extracted_file_path"] = f'{os.getcwd()}/cache/{mod_id}/{file_id}'
        target_path = self.MIODM["extracted_file_path"]
        
        os.makedirs(target_path, exist_ok=True)

        if file_path.lower().endswith(".zip"):
            VsmFileManager.unzip_file(file_path, target_path)
        else:
            logger.warning(f"File {file_path} doesn't support .zip, ignoring extraction.")
            
        logger.debug("file_extract_to_cache() => done")


    def file_move_from_cache_and_overwrite_to_maps(self, mod_id:str, file_id:str) -> None:
        logger.debug("file_move_from_cache_and_overwrite_to_maps() ...")
        
        source = f"{os.getcwd()}/cache/{mod_id}/{file_id}"
        destination_parent = f"{os.getcwd()}/maps/{mod_id}"
        destination = f"{destination_parent}/{file_id}"

        if os.path.isdir(destination_parent):
            logger.info(f"Remove old versions of {mod_id}.")
            VsmFileManager.remove_at_path(destination_parent)

        os.makedirs(destination_parent, exist_ok=True)

        logger.info(f"Moving mod folder from cache to maps folder.")
        VsmFileManager.move_folder(source, destination)
        
        if os.path.isdir(destination):
            logger.info(f"Move success '{destination}'.")
        else:
            logger.error(f"Move failure '{destination}'.")
            
        logger.debug("file_move_from_cache_and_overwrite_to_maps() => done")