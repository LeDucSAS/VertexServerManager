import logging
from vsm.VsmFileManager import VsmFileManager


logger = logging.getLogger("VsmData")


class VsmData():

    @staticmethod
    def get_server_default_conf() -> dict:
        return VsmFileManager.read_conf_file('server_default.yaml')


    @staticmethod
    def get_installed_server_data() -> dict:
        return VsmFileManager.read_conf_file('servers.yaml')


    @staticmethod
    def get_vertex_urls() -> dict:
        return VsmFileManager.read_conf_file('vertex_urls.yaml')
