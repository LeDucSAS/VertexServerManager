import logging
import os
import yaml


logger = logging.getLogger("VsmData")


class VsmData():

    def __init__(self):
        self.SERVER_DEFAULT = VsmData.load_yaml_file('./conf/server_default.yaml')
        self.SERVERS = VsmData.load_yaml_file('./conf/servers.yaml')
        self.URLS = VsmData.load_yaml_file('./conf/vertex_urls.yaml')

    @staticmethod
    def load_yaml_file(yaml_file_path:str) -> dict:
        yaml_data = None
        if os.path.isfile(yaml_file_path):
            with open(yaml_file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
        else:
            logger.warning(f"Please check ./conf/ folder if {yaml_file_path} is here.")
        return yaml_data


    @staticmethod
    def write_yaml_file(yaml_file_path:str, yaml_data:dict) -> dict:
        with open(yaml_file_path, "w") as file:
            yaml.dump(yaml_data, file)


    @staticmethod
    def load_conf_file(conf_file_name:str) -> dict:
        return VsmData.load_yaml_file(f"./conf/{conf_file_name}")


    @staticmethod
    def write_conf_file(conf_file_name:str, yaml_data:dict) -> dict:
        return VsmData.write_yaml_file(f"./conf/{conf_file_name}", yaml_data)

