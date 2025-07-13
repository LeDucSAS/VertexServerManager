# LeDucSAS - Vertex Server Manager (VSM)
# License : Free art license 1.3 https://artlibre.org/

import argparse
import logging
import os
import sys
from sys import platform
import subprocess
import time
from vsm.IniFileEditor import IniFileEditor
from vsm.VertexServerManager import VertexServerManager
from vsm.VsmFileManager import VsmFileManager
from vsm.VsmTask import VsmTask
from vsm.VsmTaskExecutor import VsmTaskExecutor
from vsm.VsmTaskType import VsmTaskType


logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)04d:%(levelname)-8s: %(message)s')
logger = logging.getLogger("Main")


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

# Scheduler flags
parser.add_argument("--task", action="store_true", help="If applicable make a task and not a direct command")
parser.add_argument("--clear-cache", action="store_true", help="Clear cache")
parser.add_argument("--scheduler-start", action="store_true", help="Start the scheduler")
parser.add_argument("--scheduler-stop" , action="store_true", help="Stop the scheduler")
parser.add_argument("--clear-tasks-processed" , action="store_true", help="Remove processed tasks (wether OK or KO)")



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


vsm = VertexServerManager()
vse = VsmTaskExecutor()
ife = IniFileEditor()


# Do init
if config["init"] == True:
    do_vsm_init = VsmTask().create(VsmTaskType.CREATE_SERVER_FOLDER_STRUCTURE)
    if config["task"]:
        VsmFileManager.write_task_file(do_vsm_init)
    else:
        vse.execute(do_vsm_init)


# Do list servers
if config["list_servers"] == True:
    serverList = vsm.get_server_list_only_localname(os.getcwd())
    if serverList:
        all_started_servers = vsm.get_all_started_servers()
        print("List of installed server [offline or online] and initial starting parameters :")
        print("")
        for server_id in serverList:
            server_status = "[ offline |        ]"
            for active in all_started_servers:
                if server_id in active["server_localname"]:
                    server_status = f"[         | online ] - {active['server_mode']} mode on map {active['server_map']} with name {active['server_gamename']}"
            print(f"    {server_id} - {server_status}")
    else:
        print("No server installed.")
    print("")


# Do server install
if config["install_server"] == True:
    do_server_install = VsmTask().create(VsmTaskType.SERVER_INSTALL)
    # I highly don't recommend it on Windows since it requires admin to create symlink
    if config["task"]:
        VsmFileManager.write_task_file(do_server_install)
    else:
        vse.execute(do_server_install)


# Do start server by port number
if config["start_id"]:
    if int(config["start_id"]) > 0:
        do_server_start = VsmTask().create(VsmTaskType.SERVER_START)
        do_server_start["server_id"] = config["start_id"]

        if config["set_server_port"] is not None:
            if config["set_server_port"] > 0:
                do_server_start["server_id"] = config["set_server_port"]
        if config["set_server_name"]:
            do_server_start["server_name"] = config["set_server_name"]
        if config["set_server_map"]:
            do_server_start["server_map"] = config["set_server_map"]
        if config["set_server_mode"]:
            do_server_start["server_mode"] = config["set_server_mode"]
        if config["task"]:
            VsmFileManager.write_task_file(do_server_start)
        else:
            vse.execute(do_server_start)
    else:
        serverList = vsm.get_server_list_only_localname(os.getcwd())
        if serverList:
            print("List of installed server :")
            for server_localname in serverList: print(server_localname)
        else:
            logger.warning("No server installed.")


# Do kill server by port number
if config["kill_id"]:
    if config["kill_id"] > 0:
        do_server_stop = VsmTask().create(VsmTaskType.SERVER_STOP_BY_ID)
        do_server_stop["server_id"] = config["kill_id"]
        if config["task"]:
            VsmFileManager.write_task_file(do_server_stop)
        else:
            vse.execute(do_server_stop)
    else:
        serverList = vsm.get_server_list_only_localname(os.getcwd())
        if serverList:
            print("List of installed server :")
            for server_localname in serverList: print(server_localname)
        else:
            print("No server installed.")


# Do restart server by port number
if config["restart_id"]:
    displayServers = False
    if config["restart_id"] > 0:
        serverList = vsm.get_server_list_only_localname(os.getcwd())
        if serverList:
            displayNoIdFound = True
            for server_localname in serverList: 
                if server_localname.endswith(str(config["restart_id"])):
                    print(f"Will restart {server_localname}")
                    do_server_restart_by_localname = VsmTask().create(VsmTaskType.SERVER_RESTART_BY_LOCALNAME)
                    do_server_restart_by_localname["server_localname"] = server_localname
                    if config["task"]:
                        VsmFileManager.write_task_file(do_server_restart_by_localname)
                    else:
                        vse.execute(do_server_restart_by_localname)
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
        serverList = vsm.get_server_list_only_localname(os.getcwd())
        if serverList:
            print("List of installed server :")
            for server_localname in serverList: print(server_localname)
        else:
            print("No server installed.")


''' Desactivated because can't properly specify values unless relying on creating a config file'''
# Do start all server
# if config["start_all"]:
#   serverList = vsm.get_server_list_only_localname(os.getcwd())
#   if serverList:
#       print("Will start all servers")
#       for server_localname in serverList: vsm.start_server_by_localname(server_localname)
#   else:
#       print("No server installed.")


# Do kill all server
if config["kill_all"]:
    serverList = vsm.get_server_list_only_localname(os.getcwd())
    if serverList:
        print("Will kill all servers")
        for server_localname in serverList: 
            do_server_stop_by_localname = VsmTask().create(VsmTaskType.SERVER_STOP_BY_LOCALNAME)
            do_server_stop_by_localname["server_localname"] = server_localname
            if config["task"]:
                VsmFileManager.write_task_file(do_server_stop_by_localname)
            else:
                vse.execute(do_server_stop_by_localname)
    else:
        logger.warning("No server installed.")


# Do restart all server
if config["restart_all"]:
    serverList = vsm.get_server_list_only_localname(os.getcwd())
    if serverList:
        print("Will restart all servers")
        for server_localname in serverList: 
            do_server_restart_by_localname = VsmTask().create(VsmTaskType.SERVER_RESTART_BY_LOCALNAME)
            do_server_restart_by_localname["server_localname"] = server_localname
            if config["task"]:
                VsmFileManager.write_task_file(do_server_restart_by_localname)
            else:
                vse.execute(do_server_restart_by_localname)
    else:
        logger.warning("No server installed.")


# Update ini file
if config["ini_update_server_id"]:
    # check server exists
    if config["ini_update_server_id"] > 0:
        server_localname = vsm.find_server_localname_by_id(config["ini_update_server_id"])
        if not vsm.is_server_already_started(server_localname):
            if server_localname is not None:
                if (
                    config['ini_file']       is not None and 
                    config['ini_update_key'] is not None and
                    config['ini_new_value']  is not None
                ):
                    ife.update_ini_file_value(server_localname, config['ini_file'], config['ini_update_key'], config['ini_new_value'])
                else:
                    print("Error : Script require the 4 arguments : --ini-update-server-id, --ini-file, --ini-update-key, --ini-new-value.")
            else:
                print(f"Can't find a server with id : {config['ini_update_server_id']}")
        else:
            print(f"Server {server_localname} is already started. No .ini update will be done.")
    else:
        serverList = vsm.get_server_list_only_localname(os.getcwd())
        if serverList:
            print("List of installed server :")
            for server_localname in serverList: print(server_localname)
        else:
            logger.warning("No server installed.")


# Install new modfile
if config["install_mod"]:
    do_install_mod = VsmTask().create(VsmTaskType.MOD_INSTALL)
    do_install_mod["mod_url"] = config["install_mod"]
    if config["task"]:
        VsmFileManager.write_task_file(do_install_mod)
    else:
        vse.execute(do_install_mod)


# Start task scheduler
if config["scheduler_start"]:
    print("Just in case, forcing stop of any scheduler")
    vse.execute(VsmTask().create(VsmTaskType.SCHEDULER_STOP))
    time.sleep(5)
    print("Executing scheduler")
    vse.execute(VsmTask().create(VsmTaskType.SCHEDULER_START))
    scheduler_starter_path = os.path.abspath(f"./scheduler_starter.py")

    if platform == "linux" or platform == "linux2":
        # Need to check
        server = subprocess.Popen([
            f"uv run {scheduler_starter_path}"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    elif platform == "win32":
        # Execute as a background task
        server = subprocess.Popen([
            "uv",
            "run",
            scheduler_starter_path
        ],
        startupinfo=subprocess.STARTUPINFO(
            dwFlags=subprocess.STARTF_USESHOWWINDOW,
            wShowWindow=subprocess.SW_HIDE,
        ),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW,
        shell=True)
    print(server)


# Stop task scheduler
if config["scheduler_stop"]:
    do_scheduler_stop = VsmTask().create(VsmTaskType.SCHEDULER_STOP)
    if config["task"]:
        VsmFileManager.write_task_file(do_scheduler_stop)
    else:
        vse.execute(do_scheduler_stop)


# Stop task scheduler
if config["clear_cache"]:
    do_clear_cache = VsmTask().create(VsmTaskType.CLEAR_CACHE)
    if config["task"]:
        VsmFileManager.write_task_file(do_clear_cache)
    else:
        vse.execute(do_clear_cache)


# Remove processed tasks
if config["clear_tasks_processed"]:
    do_delete_processed_tasks = VsmTask().create(VsmTaskType.CLEAR_TASKS_PROCESSED)
    if config["task"]:
        VsmFileManager.write_task_file(do_delete_processed_tasks)
    else:
        vse.execute(do_delete_processed_tasks)

