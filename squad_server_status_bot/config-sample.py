BOT_TOKEN                       = "BOT TOKEN HERE"
BOT_CMD_PREFIX                  = "}" # unused

# Server info messages
UPDATE_INTERVAL_SECONDS         = 60
SERVER_INFO_CHANNEL_ID          = 658822233128566794

# Server details
SERVER_DETAILS                  = [
    # HOST          , QPORT, GAME_PORT, FALLBACK NAME
    ("167.88.11.228", 27165, 7787,      "Fear and Terror #1"), # public 1 (NYC)
    ("104.194.8.111", 27165, 7787,      "Fear and Terror #2"), # public 2 (LA)
    ("104.194.8.111", 27195, 7790,      "Fear and Terror #3"), # public 3 (LA)
    ("185.38.151.16", 27165, 7787,      "Fear and Terror EU"), # public EU
]

# Database
DATABASE_FILENAME               = "database.fs"


#####################################
# DO NOT EDIT BELOW
#####################################

from dataclasses import dataclass

@dataclass
class Server():
    host : str
    qport : int
    game_port : int
    fallback_name : str

servers = []
for details in SERVER_DETAILS:
    servers.append(Server(*details))

def init_config(_bot):
    global bot
    bot = _bot
    global server_channel
    server_channel = bot.get_channel(SERVER_INFO_CHANNEL_ID)
