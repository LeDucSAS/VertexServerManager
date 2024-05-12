#!/usr/bin/env python
# LeDucSAS - Vertex Server Manager (VSM)
# License : Free art license 1.3 https://artlibre.org/

from sys import platform
if platform == "darwin":
    print("MacOS/OSX not supported since no version exists or is planned for it.")
    print("Script will terminate.")
    sys.exit() 

'''


ARGPARSE AREA


'''

# Argparse data structure
'''
{
    'init'                 : False, # Boolean automatic set
    'install_server'       : False, # Boolean automatic set
    'list_servers'         : False, # Boolean automatic set
    'start_id'             : None,  # int
    'kill_id'              : None,  # int
    'restart_id'           : None,  # int
    'kill_all'             : False, # Boolean automatic set
    'restart_all'          : False, # Boolean automatic set
    'set_server_name'      : None,  # str
    'set_server_port'      : None,  # int
    'set_server_map'       : None,  # str
    'set_server_mode'      : None,  # str
    'ini_update_server_id' : None,  # int
    'ini_file'             : None,  # str
    'ini_update_key'       : None,  # str
    'ini_new_value'        : None,  # str
    'install_mod'          : None   # str (URL)
}
'''


import argparse
import sys

parser = argparse.ArgumentParser( description="LeDucSAS - Vertex Server Manager", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Setup and installation
parser.add_argument("--init"          , action="store_true", help="Initialize the folder by creating ./cache/, ./servers/ and ./maps/ folder.")
parser.add_argument("--install-server", action="store_true", help="Download and install a new server")
# parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")

# Get server status list
parser.add_argument("-l", "--list-servers", action="store_true", help="List installed servers and execution status")

# Server start, stop, restart
parser.add_argument('-s', '--start-id'  , nargs='?', const=-1, type=int, help="Start server by port")
parser.add_argument('-k', '--kill-id'   , nargs='?', const=-1, type=int, help="Restart server by port")
parser.add_argument('-r', '--restart-id', nargs='?', const=-1, type=int, help="Restart server by port")

# parser.add_argument('--start-all', action="store_true", help="Start server by port")
parser.add_argument('--kill-all'   , action="store_true", help="Restart server by port")
parser.add_argument('--restart-all', action="store_true", help="Restart server by port")

# Server configuration
parser.add_argument('--set-server-name', nargs='?', const=None, type=str, help="Force non default game server name")
parser.add_argument('--set-server-port', nargs='?', const=None, type=int, help="Force non default game server port")
parser.add_argument('--set-server-map' , nargs='?', const=None, type=str, help="Force non default game server map")
parser.add_argument('--set-server-mode', nargs='?', const=None, type=str, help="Force non default game server gamemode")

# .INI file updates
parser.add_argument('--ini-update-server-id', nargs='?'          , const=None, type=int, help="Select the server to be updated")
parser.add_argument('--ini-file'            , nargs='?'          , const=None, type=str, help="Select the file to be updated")
parser.add_argument('--ini-update-key'      , nargs='?'          , const=None, type=str, help="Select the key to be updated")
parser.add_argument('--ini-new-value'       , nargs='?'          , const=None, type=str, help="Define the new value")

# Mod installation from mod.io
parser.add_argument('--install-mod', nargs='?', const=None, type=str, help="Input URL of mod.io file to download")


# Save and make parser
args = parser.parse_args()
config = vars(args)

# Display help by default if no argument is given
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)




'''


Command line arguments interpretation


'''
from vsm.VertexServerManager import VertexServerManager
vsm = VertexServerManager()

# Server parameter
if config["set_server_name"]:
    vsm.DATA['gameServer_name'] = config["set_server_name"]

if config["set_server_port"] is not None:
    if config["set_server_port"] > 0:
        vsm.DATA['gameServer_port'] = config["set_server_port"]

if config["set_server_map"]:
    vsm.DATA['gameServerMap'] = config["set_server_map"]

if config["set_server_mode"]:
    vsm.DATA['gameServerMode'] = config["set_server_mode"]


# Do init
if config["init"] == True:
    vsm.create_server_folder_structure()

# Do list servers
if config["list_servers"] == True:
    import os
    serverList = vsm.get_server_list_only_name(os.getcwd())
    if serverList is not None:
        all_started_servers = vsm.get_all_started_servers()
        print("List of installed server :")
        for server_name in serverList:
            server_status = "[ offline |        ]"
            for active in all_started_servers:
                if server_name in active["server_name"]:
                    server_status = "[         | online ]"
            print(f"    {server_status} - {server_name}")
    else:
        print("No server installed.")

# Do server install
if config["install_server"] == True:
    from sys import platform
    if platform == "linux" or platform == "linux2":
        vsm.install_game_server()
    elif platform == "win32":
        # Need to execute as admin because of symbolic linking map folder.
        print("\n")
        print("Windows script initialization need to execute as admin because of symbolic linking map folder.")
        print("Basically, it link once a common './maps/' to './servers/GameServerXXXXX/UserCreatedContent/maps/'.")
        print("Anything in ./maps/ folder is common to all other servers and do not need to dupplicates.")
        print("\n")

        import ctypes, sys
        def is_admin():
            try:
                is_admin_value = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin_value:
                    print("Script will now ask for admin privilege.\n")
                    input("Press ENTER to continue or CTRL+C to exit.\n\n")
                return is_admin_value
            
            except:
                return False

        if is_admin():
            print("---------------------------\n")
            print("Vertex MCS Server installation procedure starts.\n")
            try:
                vsm.install_game_server()
            except:
                input("\nAn error occured. Press enter to exit script.")
            
            input("\nCourtesy input action to read logs.\nPress enter to terminate the script whenever you want.\n\n")
        else:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    


# Do start server by port number
if config["start_id"]:
    if config["start_id"] > 0:
        vsm.start_server_by_id(config["start_id"])
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Do kill server by port number
if config["kill_id"]:
    if config["kill_id"] > 0:
        vsm.kill_server_by_id(config["kill_id"])
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Do restart server by port number
if config["restart_id"]:
    displayServers = False
    if config["restart_id"] > 0:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            displayNoIdFound = True
            for server_name in serverList: 
                if server_name.endswith(str(config["restart_id"])):
                    print(f"Will restart {server_name}")
                    vsm.restart_server_by_name(server_name)
                    displayNoIdFound = False
                    break
            if displayNoIdFound:
                print(f'No server found with id {config["restart_id"]}')
                displayServers = True
        else:
            print("No server started.")
            displayServers = True
    else:
        displayServers = True

    if displayServers:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")

''' Desactivated because can't properly specify values unless relying on creating a config file'''
# Do start all server
# if config["start_all"]:
#   import os
#   serverList = vsm.get_server_list_only_name(os.getcwd())
#   if serverList is not None:
#       print("Will start all servers")
#       for server_name in serverList: vsm.start_server_by_name(server_name)
#   else:
#       print("No server installed.")


# Do kill all server
if config["kill_all"]:
    import os
    serverList = vsm.get_server_list_only_name(os.getcwd())
    if serverList is not None:
        print("Will kill all servers")
        for server_name in serverList: 
            vsm.kill_server_by_name(server_name)
    else:
        print("No server installed.")


# Do restart all server
if config["restart_all"]:
    import os
    serverList = vsm.get_server_list_only_name(os.getcwd())
    if serverList is not None:
        print("Will restart all servers")
        for server_name in serverList: 
            vsm.restart_server_by_name(server_name)
    else:
        print("No server installed.")


# Update ini file
if config["ini_update_server_id"]:
    # check server exists
    if config["ini_update_server_id"] > 0:
        server_name = vsm.find_server_name_by_id(config["ini_update_server_id"])
        if not vsm.is_server_already_started(server_name):
            if server_name is not None:
                if (
                    config['ini_file']       is not None and 
                    config['ini_update_key'] is not None and
                    config['ini_new_value']  is not None
                ):
                    vsm.update_ini_file_value(server_name, config['ini_file'], config['ini_update_key'], config['ini_new_value'])
                else:
                    print("Error : Script require the 4 arguments : --ini-update-server-id, --ini-file, --ini-update-key, --ini-new-value.")
            else:
                print(f"Can't find a server with id : {config['ini_update_server_id']}")
        else:
            print(f"Server {server_name} is already started. No .ini update will be done.")
    else:
        import os
        serverList = vsm.get_server_list_only_name(os.getcwd())
        if serverList is not None:
            print("List of installed server :")
            for server_name in serverList: print(server_name)
        else:
            print("No server installed.")


# Install new modfile
if config["install_mod"]:
    vsm.install_mod(config["install_mod"])
