import logging
import os
import yaml


logger = logging.getLogger("VsmData")


class VsmData():

    def __init__(self):
        self.SERVER_DEFAULT = self.load_yaml_file('./conf/server_default.yaml')
        self.SERVERS = self.load_yaml_file('./conf/servers.yaml')
        self.URLS = self.load_yaml_file('./conf/vertex_urls.yaml')


    def load_yaml_file(self, yaml_file_path:str) -> dict:
        yaml_data = None
        if os.path.isfile(yaml_file_path):
            with open(yaml_file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
        else:
            logger.warning(f"Please check ./conf/ folder if {yaml_file_path} is here.")
        return yaml_data

