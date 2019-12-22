#!/usr/bin/env python3

from steam import SteamQuery

HOST = "167.88.11.228"
PORT = 27165

server_obj = SteamQuery(HOST, PORT)

# This will store the last results so you dont need to query again
#return_dictionary = server_obj.return_last_data()

# New results, also saved and can be retrieved via the return_last_data method
return_dictionary = server_obj.query_game_server()

#return_dictionary {
#   'online': True,
#   'ip': 'ip',
#   'port': port,
#   'name': 'name',
#   'map': 'map',
#   'game': 'game',
#   'description': 'server desc',
#   'players': players,
#   'max_players': slots,
#   'bots': bots,
#   'password_required': bool,
#   'vac_secure': bool,
#   'server-type': 'type',
#   'os': 'os'
#   }

print(return_dictionary)

