import sys
from sys import platform
import tarfile
import zipfile
import requests
import os
import shutil

class ModioDownloadManager():

    DATA = {}

    def __init__(self, yaml_data):
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
    

    def mod_list(self):
        # list all, list available, list installed
        ...


    def mod_install_direct_url(self, direct_mod_file_url_to_download):
        print("mod_install_direct_url() ...")
        try:
            game_id = direct_mod_file_url_to_download.split("/games/")[1].split("/")[0]
            if not (int(self.DATA["game_id"]) == int(game_id)):
                return False
            self.DATA["mod_id"] = direct_mod_file_url_to_download.split("/mods/")[1].split("/")[0]
            self.DATA["file_id"] = direct_mod_file_url_to_download.split("/files/")[1].split("/")[0]
            self.DATA["archive_url"] = f"https://api.mod.io/v1/games/{self.DATA['game_id']}/mods/{self.DATA['mod_id']}/files/{self.DATA['file_id']}/download?api_key={self.DATA['api_key']}"
        except:
            print("An exception occurred")
            return False

        # self.cachePurification() # Enable for purity of cache
        self.cacheCleanup(self.DATA["mod_id"])
        self.file_download_to_cache(self.DATA["archive_url"], self.DATA["mod_id"])
        self.file_extract_to_cache(self.DATA["downloaded_file_path"], self.DATA["mod_id"])
        self.file_move_from_cache_and_overwrite_to_maps(self.DATA["mod_id"])
        self.cacheCleanup(self.DATA["mod_id"])
        
        print("mod_install_direct_url() => done")


    def cacheCleanup(self, mod_id):
        print("cacheCleanup() ...")
        cached_file = f"{os.getcwd()}/cache/{self.DATA["archive_name"]}"
        cached_folder = f"{os.getcwd()}/cache/{mod_id}/"
        if os.path.isfile(cached_file):
            os.remove(cached_file)
        if os.path.isdir(cached_folder):
            shutil.rmtree(cached_folder)
        print("cacheCleanup() => done")


    def cachePurification(self):
        print("cachePurification() ...")
        retain = [".gitignore"]
        cache_path = f"{os.getcwd()}/cache/"
        for item in os.listdir(cache_path):
            if item not in retain:  
                item_path = f"{cache_path}{item}"
                if os.path.isfile(item_path):
                    os.remove(item_path)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        print("cachePurification() => done")


    def file_download_to_cache(self, url_to_download, filename):
        print("file_download_to_cache() ...")
        # Getting the file data
        response = requests.get(url_to_download, stream=True, allow_redirects=True)

        self.DATA["archive_type"] = response.headers.get("Content-Type").split("/")[1]
        self.DATA["archive_name"] = response.url.split("?")[0].split("/")[-1]
        self.DATA["downloaded_file_path"] = f"cache/{self.DATA["archive_name"]}"

        with open(self.DATA["downloaded_file_path"], 'wb') as fd:
            print(f'Downloading {self.DATA["downloaded_file_path"]}')
            total_length = response.headers.get('content-length')
            if total_length is None: # no content length header
                fd.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    fd.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
                print() # To have a clean newline
        print("file_download_to_cache() => done")


    def file_extract_to_cache(self, file_path, mod_id):
        print("file_extract() ...")
        # Create a folder with the ID of the mod so it easier to update
        self.DATA["extracted_file_path"] = f'{os.getcwd()}/cache/{mod_id}'
        target_path = self.DATA["extracted_file_path"]
        os.mkdir(target_path)
        file_ext = self.DATA["archive_name"].split(".")
        if file_ext == "zip":
            self.__unzip_file(file_path, target_path)
        print("file_extract() => done")


    def file_move_from_cache_and_overwrite_to_maps(self, mod_id):
        print("file_move_from_cache_and_overwrite_to_maps() ...")
        source = f"{os.getcwd()}/cache/{mod_id}"
        destination = f"{os.getcwd()}/maps/{mod_id}"
        if os.path.isdir(destination):
            print(f"Warning : Deleting pre-existing '{destination}'.")
            shutil.rmtree(destination)
        print(f"Info : Moving mod folder from cache to maps folder'.")
        shutil.move(source, destination)
        if os.path.isdir(destination):
            print(f"Info : Copy success '{destination}'.")
        print("file_move_from_cache_and_overwrite_to_maps() => done")


    def __untargz_file(self, tarGzFilePath, extractTargetPath):
        fileExtractor = tarfile.open(tarGzFilePath)
        fileExtractor.extractall(extractTargetPath)
        fileExtractor.close()
        

    def __unzip_file(self, zipFilePath, extractTargetPath):
        with zipfile.ZipFile(zipFilePath, 'r') as zip_ref:
            zip_ref.extractall(extractTargetPath)

