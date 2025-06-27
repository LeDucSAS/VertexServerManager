import logging
import os
import yaml


logger = logging.getLogger("VsmData")


class VsmData():

    def __init__(self):
        self.DATA = None
        self.DATA = self.load_yaml_file('./conf/servers.yaml')


    def load_yaml_file(self, yaml_file_path):
        yaml_data = None
        if os.path.isfile(yaml_file_path):
            with open(yaml_file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
        else:
            logger.info(f"Please check ./conf/ folder if {yaml_file_path} is here.")
        return yaml_data

