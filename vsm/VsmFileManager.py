import os
import shutil
import tarfile
import zipfile
import logging
logger = logging.getLogger("VsmFileManager")

class VsmFileManager():

    def __init__(self):
        ...


    def cache_mod_cleanup(self, cached_folder, cached_file):
        logger.debug("cacheCleanup() ...")
        self.remove_at_path(cached_folder)
        self.remove_at_path(cached_file)
        logger.debug("cacheCleanup() => done")


    def cache_purification(self):
        logger.debug("cache_purification() ...")
        folder_path = f"{os.getcwd()}/cache/"
        retain_files = [".gitignore"]
        self.__folder_purification(folder_path, retain_files)
        logger.debug("cache_purification() done")


    def __folder_purification(self, folder_to_purify, retain_files = []):
        logger.debug("__folder_purification() ...")
        for item in os.listdir(folder_to_purify):
            if item not in retain_files:
                self.remove_at_path(f"{folder_to_purify}{item}")
        logger.debug("__folder_purification() done")


    def remove_at_path(self, path_to_remove):
        logger.debug("remove_at_path() ...")
        if os.path.isfile(path_to_remove):
            logger.info(f"Removing file : {path_to_remove}")
            os.remove(path_to_remove)
        elif os.path.isdir(path_to_remove):
            logger.info(f"Removing dir : {path_to_remove}")
            shutil.rmtree(path_to_remove)
        else: 
            logger.info(f"Nothing to remove at : {path_to_remove}")
        logger.debug("remove_at_path() done")


    def untargz_file(self, tarGzFilePath, extractTargetPath):
        logger.debug("untargz_file() ...")
        logger.info(f"Untargzing {tarGzFilePath} to {extractTargetPath}")
        fileExtractor = tarfile.open(tarGzFilePath)
        fileExtractor.extractall(extractTargetPath)
        fileExtractor.close()
        logger.debug("untargz_file() done")


    def unzip_file(self, zipFilePath, extractTargetPath):
        logger.debug("unzip_file() ...")
        logger.info(f"Unzipping {zipFilePath} to {extractTargetPath}")
        with zipfile.ZipFile(zipFilePath, 'r') as zip_ref:
            zip_ref.extractall(extractTargetPath)
        logger.debug("unzip_file() done")


    def move_folder(self, source_dir, destination_dir):
        logger.debug("move_folder() ...")
        logger.info(f"Moving {source_dir} to {destination_dir}")
        shutil.move(source_dir, destination_dir)
        logger.debug("move_folder() done")


    def create_symlink(self, symlink_source_path, symlink_target_path):
        os.symlink(
            os.path.abspath(symlink_source_path), 
            os.path.abspath(symlink_target_path)
        )
        return True

