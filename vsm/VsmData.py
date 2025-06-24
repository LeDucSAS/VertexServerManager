import logging
import os
import yaml


logger = logging.getLogger("VsmData")


class VsmData():
    def __init__(self):
        self.DATA = None
        server_conf_file = './conf/servers.yaml'

        if os.path.isfile(server_conf_file):
            with open(server_conf_file, 'r') as file:
                self.DATA = yaml.safe_load(file)
        else:
            print(f"Please check ./conf/ folder if {server_conf_file} is here.")

