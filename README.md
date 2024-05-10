# LeDucSAS - Vertex server manager
Command line tool and class to be used for Vertex game server management (https://playvertex.com/).

License Art Libre 1.3 (https://artlibre.org/).

> **Modules to install**
* psutil
* requests

> **Note**
> About OS support
* Linux support (tested Ubuntu 22.04.2 LTS and Python 3.10)
* Windows - Planned
* MacOS - Not planned yet

> **Note**
> The script ends after executing each command, it does not run as a process persistently or a service.


## Purpose and functional specification
This tool should be able to
- Work as comand line execution only, be callable from other utilities (like discord bot)
- Consider the directory he's inside as the root of the server folder structure
- Setup/create a global server folder structure
- Create and install server instances
- Start server on demand
- Stop server on demand
- Restart server on demand
- Restart all
- Kill all
- Make mutualized folder for mods
- Customize server launch command line arguments (port, server name, map, gamemode)
- Update ini files values (like Game.ini)
- Download mods from vertex mod.io repository

> **Warning**
> You have to do port management yourself (sudo ufw ...)



## User guide

0. Choose a directory you want to be your server manager root.
1. Put `vsm.py` in empty directory. To be able to update the file easily you can use git clone to create a VertexServerManager folder;
```console
~$ git clone https://github.com/LeDucSAS/VertexServerManager/
```
2. Init directory to create required folders : `./cache/` (for download and unzip), `./servers/` (to store servers instances), `./maps/` (common folder for every server in order to save disk space, it is done as creating a symlink from `./maps/` to each `./servers/GameServerXXXXX/MCS/UserCreatedContent/maps`).
```console
~$ ls -1p --group-directories-first
README.md
vsm.py

~$ python3 vsm.py --init
Check that path has not been initialized already.
    ->  Current directory has been init for vertex servers

~$ ls -1p --group-directories-first
cache/
maps/
servers/
README.md
vsm.py
```
3. Install as much server as you want. Each server will be created fallowing "Name+ID" rule (Ex: GameServer27070). By default ID = default port (here ID = 27070). 
```console
~$ python3 vsm.py --install-server
```
4. Start a server using `--start-id` or `-s` (note : `--start-id 27070` is a shortcut to select `GameServer27070`). Also if the server is already started it won't start it twice. `--set-server-name` is pretty explicit. 
```console
# The minimum you need (default open mode on ocean complex)
~$ python3 vsm.py \
--start-id 27070 \
--set-server-name "Server number 1" 
```
5. `--set-server-map` define the map you want. `--set-server-mode` define the mode you want. To force another port than default use `--set-server-port`. You still kill it with the same ID (ex: 27070 because its server name GameServer27070) even though you forced another port (ex: 4242). 
```console
# The maximum you can
~$ python3 vsm.py \
--start-id 27070 \
--set-server-name "Server number 1" \
--set-server-map LEDUCSAS_VERTEX_TEMPLE \
--set-server-mode DUEL \
--set-server-port 4242

# Will execute as
./servers/GameServer27070/MCS/Binaries/Linux/MCSServer LEDUCSAS_VERTEX_TEMPLE?game=DUEL -port=4242 -servername='Server number 1'
```
6. Some straightforward commands.
```console
~$ python3 vsm.py --kill-id 27070 # or -k 27070
~$ python3 vsm.py --restart-id 27070 # or -r 27070
~$ python3 vsm.py --restart-all
~$ python3 vsm.py --kill-all
```
7. You can update ini files, as security will not execute if server is live (since server shutdown overwrite some ini files).
```console
~$ python3 vsm.py \
--ini-update-server-id 27070 \
--ini-file Game.ini \
--ini-update-key RequiresPassword \
--ini-new-value False
```
8. You can download mods from mod.io. The link to be used has to be found on the new mod.io website. For example on https://mod.io/g/vertex/m/leducsas-cosmos you have the side section titled _Download files manually_ on which you have `File <icon_release_note> <icon_download>`. You have to right click on `<icon_download>` and copy paste the link (currently https://api.mod.io/v1/games/594/mods/1780746/files/2779135/download); it is that link that has to be passed to `--install-mod` as argument.
```console
~$ python3 vsm.py --install-mod https://api.mod.io/v1/games/594/mods/1780746/files/2779135/download
```

9. You can also list the current installed servers and get their activity status with `-l` or `--list-servers`.
```console
~$ python .\vsm.py -l
List of installed server :
    [ offline |        ] - GameServer27070
    [ offline |        ] - GameServer27071
    [ offline |        ] - GameServer27072
    [ offline |        ] - GameServer27073
    [ offline |        ] - GameServer27074
    [ offline |        ] - GameServer27075
    [ offline |        ] - GameServer27076
    [         | online ] - GameServer27077
    [ offline |        ] - GameServer27078
```
Feedback much appreciated !

Your sincerely,
LeDucSAS
