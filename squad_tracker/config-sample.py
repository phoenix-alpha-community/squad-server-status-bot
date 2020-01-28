BOT_TOKEN                       = "BOT TOKEN HERE"
BOT_CMD_PREFIX                  = "!"
MESSAGE_DELETE_DELAY_SECONDS    = 60

# Server info messages
UPDATE_INTERVAL_SECONDS         = 60
SERVER_INFO_CHANNEL_ID          = 665048711403143168

# TK tracker
MQTT_ADDRESS                    = ("MQTT BROKER IP HERE", 1883)
MQTT_SUB_USER                   = "SUBSCRIBER USERNAME HERE"
MQTT_SUB_PASSWORD               = "SUBSCRIBER PASSWORD HERE"
MQTT_PUB_USER                   = "PUBLISHER USERNAME HERE"
MQTT_PUB_PASSWORD               = "PUBLISHER PASSWORD HERE"
MQTT_TOPIC                      = "squad-tks"

# Server details
SERVER_DETAILS                  = [
    # HOST          , QPORT, BASE DIRECTORY              , TK CHANNEL
    ("167.88.11.228", 27165, r"C:\servers\Squad_Server",   665048744219115520),
    ("167.88.11.228", 27175, r"C:\servers\Squad_Server_2", 669304088248188949),
    ("167.88.11.228", 27195, r"C:\servers\Squad_Server_4", 669304112684335124),
]

# Database
DATABASE_FILENAME               = "database.fs"
ADMINCAM_LOG_FILENAME           = "admincam.log"


#####################################
# DO NOT EDIT BELOW
#####################################

import pytz
from dataclasses import dataclass

TIMEZONE = pytz.timezone("US/Eastern")

@dataclass
class Server():
    host : str
    qport : int
    base_dir : str
    tk_channel_id : int

servers = []
for host, qport, base_dir, tk_channel_id in SERVER_DETAILS:
    servers.append(Server(host, qport, base_dir, tk_channel_id))

def init_config(_bot):
    global bot
    bot = _bot
    global server_channel
    server_channel = bot.get_channel(SERVER_INFO_CHANNEL_ID)
