BOT_TOKEN = "BOT TOKEN HERE"

BOT_CMD_PREFIX                  = "!"
MESSAGE_DELETE_DELAY_SECONDS    = 60

# Server info messages
UPDATE_INTERVAL_SECONDS         = 60
SERVER_CHANNEL_ID               = 665048711403143168
SERVERS                         = [
                                    ("167.88.11.228", 27165), # Public #1
                                    ("167.88.11.228", 27175), # Public #2
                                    ("167.88.11.228", 27195), # Public #3
                                  ]

# Seeding pings
SEEDING_PING_TIMES_HOURS_EST    = [12, 16, 20] # 12pm, 4pm, 8pm
POPPER_CHANNEL_ID               = 665048726003384360
POPPER_ROLE_ID                  = 664857094331301931
POPPING_PLAYER_THRESHOLD        = 30

# TK tracker
TK_CHANNEL_ID                   = 665048744219115520
MQTT_ADDRESS                    = ("MQTT BROKER IP HERE", 1883)
MQTT_SUB_USER                   = "SUBSCRIBER USERNAME HERE"
MQTT_SUB_PASSWORD               = "SUBSCRIBER PASSWORD HERE"
MQTT_PUB_USER                   = "PUBLISHER USERNAME HERE"
MQTT_PUB_PASSWORD               = "PUBLISHER PASSWORD HERE"
MQTT_TOPIC                      = "squad-tks"
SERVER_BASE_DIRS                = [
                                    r"C:\servers\Squad_Server",
                                    r"C:\servers\Squad_Server_2",
                                    r"C:\servers\Squad_Server_4",
                                  ]

# Database
DATABASE_FILENAME               = "database.fs"


#####################################
# DO NOT EDIT BELOW
#####################################

import pytz

TIMEZONE = pytz.timezone("US/Eastern")

def init_config(_bot):
    global bot
    bot = _bot
    global server_channel
    server_channel = bot.get_channel(SERVER_CHANNEL_ID)
    global popper_channel
    popper_channel = bot.get_channel(POPPER_CHANNEL_ID)
    guild = popper_channel.guild
    global popper_role
    popper_role = guild.get_role(POPPER_ROLE_ID)
    global tk_channel
    tk_channel = bot.get_channel(TK_CHANNEL_ID)

