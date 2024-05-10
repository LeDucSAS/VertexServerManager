#!/usr/bin/env python
# LeDucSAS - Vertex Server Manager (VSM)
# License : Free art license 1.3 https://artlibre.org/

from vsm.VertexServerManager import VertexServerManager
vsm = VertexServerManager()


vsm.get_all_started_servers()

print(vsm.is_server_already_started("27077"))