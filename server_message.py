import config
import discord
from steam import SteamQuery

class ServerMessage():

    def __init__(self, host, port, bot):
        self.__message_id = -1
        self.host = host
        self.qport = port
        self.qport2 = port + 1
        self.name = "Unknown Server"


    async def update(self, bot):
        '''Queries the server information and creates / updates the Discord
        message.
        Remember to add the ServerMessage object to the database after creating
        it.'''
        server_obj = SteamQuery(self.host, self.qport)
        quicklink = f"{self.host}:{self.qport2}"
        server_info = server_obj.query_game_server()

        channel = bot.get_channel(config.SERVER_CHANNEL)


        if server_info["online"]:
            # Save name in case server goes offline
            self.name = server_info['name']

            # Create embed
            embed = discord.Embed(title=self.name)

            # Thumbnail
            map_url_name = translate_map_name(server_info["map"])
            embed.set_thumbnail(url=f"https://squadmaps.com/full/{map_url_name}.jpg")

            # Player count
            # extra formatting for queue
            # PLAYER_COUNT / MAX_PLAYERS (+ QUEUE)
            players = min(server_info["max_players"], server_info["players"])
            queue = server_info['players'] - server_info['max_players']
            player_count_str = f"{players}/{server_info['max_players']}"
            if queue > 0:
                player_count_str += f" (+{queue})"
            embed.add_field(name='Player Count', value=player_count_str)
            embed.color = get_embed_color(players)

            # Map, Quicklink
            embed.add_field(name='Map', value=f"{server_info['map']}", inline=True)
            embed.add_field(name='Quick Connect', value=f"steam://connect/{quicklink}", inline=False)

            # Dynamic image
            #with open(r"images/bg1.jpg", "rb") as f:
            #    shit = await channel.send(file=f)
            #print(shit)
        else:
            # Server offline, use cached name
            embed = discord.Embed(title=self.name, color=0x222222)
            embed.add_field(name="Status", value="Offline")

        if self.__message_id == -1:
            # create new message
            message = await channel.send(embed=embed)
            self.__message_id = message.id
        else:
            message = await channel.fetch_message(self.__message_id)
            # TODO error handling
            await message.edit(embed=embed)


    async def delete(self, bot):
        '''Deletes the Discord message.
        Remember to delete the ServerMessage object from the database afterwards.'''
        channel = bot.get_channel(config.SERVER_CHANNEL)
        message = await channel.fetch_message(self.__message_id)
        # TODO error handling
        await message.delete()


def translate_map_name(raw_name):
    '''Translates map names supplied by SteamQuery into their file names on
    squadmaps.com'''
    if raw_name == "CAF_Yehorivka_TC_V1":
        return "Yehorivka_TC_v1"
    else:
        return raw_name.replace(" ", "_")


def get_embed_color(player_count):
    if player_count >= 80:
        return 0xee2020 # RED
    if player_count >= 71:
        return 0xEE9420 # ORANGE
    if player_count >= 41:
        return 0x20EE50 # GREEN

    return 0xEE9420 # ORANGE
