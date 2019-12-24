import asyncio
import discord
import config
from steam import SteamQuery
from discord.ext import commands

bot = commands.Bot(command_prefix=config.BOT_CMD_PREFIX)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await joinkit()


HOST = "167.88.11.228"
PORT1 = 27165
PORT2 = 27175
PORT3 = 27195


async def joinkit():
    n = 0
    while n != 3:
        if n == 0:
            server_obj = SteamQuery(HOST, PORT1)
            quicklink = f"{HOST}:27166"
        if n == 1:
            server_obj = SteamQuery(HOST, PORT2)
            quicklink = f"{HOST}:27176"
        if n == 2:
            server_obj = SteamQuery(HOST, PORT3)
            quicklink = f"{HOST}:27186"
        n = n + 1
        server_info = server_obj.query_game_server()
        await embedmaker(server_info, quicklink)
    if n == 3:
        await sleeptimer()


async def embedmaker(server_info, quicklink):
    channel = bot.get_channel(config.SERVER_CHANNEL)
    if server_info['map'] == "CAF_Yehorivka_TC_V1":
        mapurl = "Yehorivka_TC_v1"
    else:
        mapurl = server_info['map'].replace(" ", "_")
    embed = discord.Embed(
        title=server_info['name']
    )
    embed.set_thumbnail(url=f"https://squadmaps.com/full/{mapurl}.jpg")
    if server_info['players'] > server_info['max_players']:
        players = server_info['players'] - server_info['max_players']
        embed.add_field(name='Played Count', value=f"{server_info['max_players']}/{server_info['max_players']} "
                                                   f"(+{players})")
    else:
        embed.add_field(name='Played Count', value=f"{server_info['players']}/{server_info['max_players']}")
    embed.add_field(name='Map', value=f"{server_info['map']}", inline=True)
    embed.add_field(name='Quick Connect', value=f"steam://connect/{quicklink}", inline=False)
    await channel.send(embed=embed)


async def sleeptimer():
    await asyncio.sleep(60)
    await joinkit()

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
