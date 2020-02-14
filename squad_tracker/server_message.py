import config
import discord
import persistent
from steam import SteamQuery

class ServerMessage(persistent.Persistent):

    def __init__(self, host, qport, game_port, bot):
        self.__message_id = -1
        self.host = host
        self.qport = qport
        self.qport2 = qport + 1
        self.game_port = game_port
        self.name = "Unknown Server"
        self.cur_map = "Unknown Map"

    def __eq__(self, other):
        return self.__message_id == other.__message_id

    def __lt__(self, other):
        return self.__message_id < other.__message_id

    def __hash__(self):
        return hash(self.__message_id)


    async def update(self, bot):
        '''Queries the server information and creates / updates the Discord
        message.
        Remember to add the ServerMessage object to the database after creating
        it.'''
        server_obj = SteamQuery(self.host, self.qport)
        quicklink = f"{self.host}:{self.game_port}"
        server_info = server_obj.query_game_server()
        print(self.qport, server_info)

        channel = config.server_channel


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
            self.cur_map = server_info['map']
            embed.add_field(name='Quick Connect', value=f"steam://connect/{quicklink}", inline=False)

            # Dynamic image
            #with open(r"images/bg1.jpg", "rb") as f:
            #    shit = await channel.send(file=f)
            #print(shit)
        else:
            # Server offline, use cached name
            embed = discord.Embed(title=self.name, color=0x222222)
            embed.add_field(name="Status", value="Offline")

        if self.__message_id != -1:
            try:
                message = await channel.fetch_message(self.__message_id)
                await message.edit(embed=embed)
                return
            except discord.errors.NotFound as e:
                print(f"[WARN] Deletion of message from server {self.name} "
                      f"not tracked.")

        # create new message
        message = await channel.send(embed=embed)
        self.__message_id = message.id


    async def delete(self, bot):
        '''Deletes the Discord message.
        Remember to delete the ServerMessage object from the database afterwards.'''
        channel = config.server_channel
        try:
            message = await channel.fetch_message(self.__message_id)
            await message.delete()
        except discord.errors.NotFound as e:
            print(f"[WARN] Deletion of message from server {self.name} "
                    f"not tracked.")


def translate_map_name(name):
    '''Translates map names supplied by SteamQuery into their file names on
    squadmaps.com'''
    # Strip prefixes
    name = name.replace("CAF_", "")
    name = name.replace("SPM_", "")
    name = name.replace("HC_", "")

    # Replace spaces
    name = name.replace(" ", "_")

    # Change some map names
    name = name.replace("LogarValley", "Logar_Valley")
    name = name.replace("FoolsRoad_AAS_v2", "Fool's_Road_AAS_v1")

    return name


def get_embed_color(player_count):
    if player_count >= 41:
        return 0x20EE50 # GREEN, popped
    if player_count >= 1:
        return 0xEE9420 # ORANGE, not popped
    if player_count == 0:
        return 0xee2020 # RED, dead
