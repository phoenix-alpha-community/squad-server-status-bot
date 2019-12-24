#!/usr/bin/env python3

import asyncio
import config
import discord
import traceback
import pytz
from database import Database
from datetime import datetime
from discord.ext import commands
from server_message import ServerMessage

bot = commands.Bot(command_prefix=config.BOT_CMD_PREFIX)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    asyncio.ensure_future(update_routine())


async def update_messages():
    db = Database.load()
    server_messages = db.server_messages

    # delete unwanted messages
    deleted_messages = set()
    for m in server_messages:
        if m.qport not in config.PORTS:
           await m.delete(bot)
           deleted_messages.add(m)
    server_messages -= deleted_messages

    # update existing messages
    updated_ports = set()
    for m in server_messages:
        await m.update(bot)
        updated_ports.add(m.qport)

    # create new messages
    for qport in config.PORTS:
        if qport not in updated_ports:
            m = ServerMessage(config.HOST, qport, bot)
            await m.update(bot)
            server_messages.add(m)

    db.save()


async def update_routine():
    while True:
        # Try-catch to avoid crashing all updates on error
        try:
            time = datetime.now(pytz.timezone("US/Eastern"))
            time_str = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str} EST] Updating {config.PORTS}")

            await update_messages()
        except Exception as e:
            traceback.print_exception(e)

        await asyncio.sleep(config.UPDATE_INTERVAL_SECONDS)

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
