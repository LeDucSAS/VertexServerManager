import configparser
import os
import ast
import logging


logger = logging.getLogger("IniFileEditor")


class IniFileEditor():

    def __init__(self):
        ...
    """

    Class Structure
    -- Global data
    Data
    def __init__(self):
    
    def update_ini_file_value             (self, server_localname, ini_filename, key_to_update, new_value):

    """
    def update_ini_file_value(self, server_localname, ini_filename, key_to_update, new_value):
        
        ini_file_path = "./servers/<SERVER_LOCALNAME>/MCS/Saved/Config/LinuxServer/<INI_FILENAME>"
        ini_file_path = ini_file_path.replace("<SERVER_LOCALNAME>", server_localname)
        ini_file_path = ini_file_path.replace("<INI_FILENAME>", ini_filename)

        if not os.path.exists(ini_file_path):
            logger.info(f"File '{ini_file_path}' not found.")
            return False

        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read(ini_file_path)

        key_has_been_found = False
        for section in config_parser.sections():
            section_dict = dict(config_parser.items(section))
            for key in section_dict:
                if key == key_to_update:
                    key_has_been_found = True
                    original_value = section_dict[key]
                    eval_ini_value = None
                    eval_new_value = None

                    try:
                        eval_ini_value = ast.literal_eval(section_dict[key])
                    except:
                        eval_ini_value = section_dict[key]

                    try:
                        eval_new_value = ast.literal_eval(new_value)
                    except:
                        eval_new_value = new_value

                    type_of_ini_value = type(eval_ini_value)
                    type_of_new_value = type(eval_new_value)

                    if type_of_new_value is type_of_ini_value:
                        config_parser.set(section, key_to_update, new_value)
                        with open(ini_file_path, 'w') as configfile:
                            config_parser.write(configfile, space_around_delimiters=False)
                            logger.info(f"Config key '{key_to_update}' of '{ini_file_path}' has been updated from '{original_value}' to '{new_value}'.")
                        break
                    else:
                        logger.info(f"Value mismatch : ini value is type '{type_of_ini_value}' and new value is type '{type_of_new_value}'.")
                        break

        if not key_has_been_found:
            logger.info(f"Config key '{key_to_update}' has not been found inside '{ini_file_path}'.")
        return key_has_been_found
