BOT_TOKEN = "BOT TOKEN HERE"
BOT_CMD_PREFIX = "}"  # unused

# Server info messages
UPDATE_INTERVAL_SECONDS = 60
SQUAD_INFO_CHANNEL_ID = 658822233128566794
POST_INFO_CHANNEL_ID = 706308588234342431

# Server details
SQUAD_SERVER_DETAILS = [
    # HOST          , QPORT, GAME_PORT, FALLBACK NAME
    ("209.222.98.15", 27165, 7787, "Fear and Terror #1 | NYC"),  # public 1 (NYC)
    ("209.222.98.15", 27205, 7791, "Fear and Terror #2 | NYC"),  # public 2 (NYC)
    ("104.194.8.111", 27195, 7790, "Fear and Terror #3 | LA"),  # public 3 (LA)
    ("185.38.151.16", 27165, 7787, "Fear and Terror EU | LON"),  # public EU
]

POST_SERVER_DETAILS = [
    ("209.222.98.15", 10037, 10027, "Fear and Terror NA | Post Scriptum #1"),  # PS 1
    ("209.222.98.15", 10087, 10057, "Fear and Terror NA | Post Scriptum #2"),  # PS 2
]
# Database
DATABASE_FILENAME = "newdatabase.fs"


#####################################
# DO NOT EDIT BELOW
#####################################

from dataclasses import dataclass


@dataclass
class Server:
    host: str
    qport: int
    game_port: int
    fallback_name: str


squadservers = []
for details in SQUAD_SERVER_DETAILS:
    squadservers.append(Server(*details))

postservers = []
for details in POST_SERVER_DETAILS:
    postservers.append(Server(*details))


def init_config(_bot):
    global bot
    bot = _bot
    global squad_server_channel
    squad_server_channel = bot.get_channel(SQUAD_INFO_CHANNEL_ID)
    global post_server_channel
    post_server_channel = bot.get_channel(POST_INFO_CHANNEL_ID)
