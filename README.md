# LeDucSAS - Vertex server manager
Command line tool and class to be used for Vertex game server management (https://playvertex.com/)

License Art Libre 1.3 (https://artlibre.org/)


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


## User guide
1. Put file in empty directory
2. Init directory to create required folders : `./cache/` (for download and unzip), `./servers/` (to store servers instances), `./maps/` (common folder for every 	instance in order to save disk space).
```bash
python3 vsm.py --init
```
3. Install as much server as you want. Each server will be created fallowing "Name+ID" rule (Ex: GameServer27070). By default ID = default port (here ID = 27070). 
```bash
python3 vsm.py --install-server
```
4. Start a server using `--start-id` or `-s` (note : `--start-id 27070` is a shortcut to select `GameServer27070`). Also if the server is already started it won't start it twice. `--set-server-name` is pretty explicit. 
```bash
# The minimum you need (default open mode on ocean complex)
python3 vsm.py \
--start-id 27070 \
--set-server-name "Server number 1" 
```
5. `--set-server-map` define the map you want. `--set-server-mode` define the mode you want. To force another port than default use `--set-server-port`. You still kill it with the same ID (ex: 27070 because its server name GameServer27070) even though you forced another port (ex: 4242).
```bash
# The maximum you can
python3 vsm.py \
--start-id 27070 \
--set-server-name "Server number 1" \
--set-server-map LEDUCSAS_VERTEX_TEMPLE \
--set-server-mode DUEL \
--set-server-port 4242
```
6. Some straightforward commands
```bash
python3 vsm.py --kill-id 27070 # or -k 27070
python3 vsm.py --restart-id 27070 # or -r 27070
python3 vsm.py --restart-all
python3 vsm.py --kill-all
```
7. You can update ini files. Won't work if server is live.
```bash
python3 vsm.py \
--ini-update-server-id 27070 \
--ini-file Game.ini \
--ini-update-key RequiresPassword \
--ini-new-value False
```
8. You can download mods from mod.io
```bash
python3 vsm.py --install-mod https://api.mod.io/v1/games/594/mods/1780746/files/2779135/download
```

Feedback much appreciated !

Your sincerely,
LeDucSAS