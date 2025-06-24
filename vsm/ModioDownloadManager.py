import requests
import os
import vsm.VsmFileManager as VsmFileManager
import logging
logger = logging.getLogger("ModioDownloadManager")

class ModioDownloadManager():

    def __init__(self, yaml_data):
        self.enable_cache_purification = True
        self.DATA = {}
        # Technical data to access the mod file
        self.DATA["game_id"] = yaml_data["game_id"]
        self.DATA["mod_id"] = ''
        self.DATA["file_id"] = ''
        self.DATA["api_key"] = yaml_data["api_key"]
        # Technical data about the file
        self.DATA["archive_url"] = ''
        self.DATA["archive_name"] = ''
        self.DATA["archive_type"] = ''
        # Local data
        self.DATA["downloaded_file_path"] = ''
        self.DATA["extracted_file_path"] = ''
        self.vfm = VsmFileManager.VsmFileManager()
    

    def mod_list(self):
        # list all, list available, list installed
        ...


    def mod_install_direct_url(self, direct_mod_file_url_to_download):
        logger.debug("mod_install_direct_url() ...")
        try:
            game_id = direct_mod_file_url_to_download.split("/games/")[1].split("/")[0]
            if not (int(self.DATA["game_id"]) == int(game_id)):
                return False
            self.DATA["mod_id"] = direct_mod_file_url_to_download.split("/mods/")[1].split("/")[0]
            self.DATA["file_id"] = direct_mod_file_url_to_download.split("/files/")[1].split("/")[0]
            self.DATA["archive_url"] = f"https://api.mod.io/v1/games/{self.DATA['game_id']}/mods/{self.DATA['mod_id']}/files/{self.DATA['file_id']}/download?api_key={self.DATA['api_key']}"
        except:
            logger.critical("An exception occurred")
            return False

        if(self.enable_cache_purification):
            self.vfm.cache_purification() # Removes everything but .gitignore
        self.file_download_to_cache(self.DATA["archive_url"], self.DATA["mod_id"])
        self.file_extract_to_cache(self.DATA["downloaded_file_path"], self.DATA["mod_id"])
        self.file_move_from_cache_and_overwrite_to_maps(self.DATA["mod_id"])
        self.vfm.cache_mod_cleanup(f"{os.getcwd()}/cache/{self.DATA["mod_id"]}/", f"{os.getcwd()}/cache/{self.DATA["archive_name"]}")
        
        logger.debug("mod_install_direct_url() => done")


    def file_download_to_cache(self, url_to_download, filename):
        logger.debug("> file_download_to_cache() ...")
        # Getting the file data
        response = requests.get(url_to_download, stream=True, allow_redirects=True)

        self.DATA["archive_type"] = response.headers.get("Content-Type").split("/")[1]
        self.DATA["archive_name"] = response.url.split("?")[0].split("/")[-1]
        self.DATA["downloaded_file_path"] = f"cache/{self.DATA["archive_name"]}"

        with open(self.DATA["downloaded_file_path"], 'wb') as fd:
            logger.info(f'Downloading {self.DATA["downloaded_file_path"]}')
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                fd.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                nextdone = 20
                logger.info("Download 0%")
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    fd.write(data)
                    done = int(100 * dl / total_length)
                    if(done == nextdone):
                        logger.info(f"Download {done}%")
                        nextdone = nextdone + 20
            logger.info(f'Downloaded {self.DATA["downloaded_file_path"]}')
        logger.debug("file_download_to_cache() => done")


    def file_extract_to_cache(self, file_path, mod_id):
        logger.debug("file_extract_to_cache() ...")
        # Create a folder with the ID of the mod so it easier to update
        self.DATA["extracted_file_path"] = f'{os.getcwd()}/cache/{mod_id}'
        target_path = self.DATA["extracted_file_path"]
        os.mkdir(target_path)
        file_ext = self.DATA["archive_name"].split(".")[1]
        if file_ext == "zip":
            self.vfm.unzip_file(file_path, target_path)
        logger.debug("file_extract_to_cache() => done")


    def file_move_from_cache_and_overwrite_to_maps(self, mod_id):
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

