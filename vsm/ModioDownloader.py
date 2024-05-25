class ModioDownloader():
    def __init__(self):
        ...
    """

    Class Structure
    -- Global data
    Data
    def __init__(self):

    
    -- mod.io
    def install_mod                       (self, mod_url_to_download):

    """
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

