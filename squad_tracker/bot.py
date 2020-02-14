#!/usr/bin/env python3

import asyncio
import config
import discord
import os.path
import pytz
import scheduling
import tk_listener
import traceback
import transaction
from BTrees.OOBTree import TreeSet
from database import db
from datetime import datetime
from discord.ext import commands
from server_message import ServerMessage

bot = commands.Bot(command_prefix=config.BOT_CMD_PREFIX)


@bot.event
async def on_ready():
    config.init_config(bot)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await tk_listener.init_tk_listener()

    scheduling.init_scheduler()

    # schedule tasks
    scheduling.interval_execute(update_messages, [],
                            interval_seconds=config.UPDATE_INTERVAL_SECONDS)
    await update_messages()


async def update_messages():
    time = datetime.now(config.TIMEZONE)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} EST] Updating server messages")

    # check if the server set changed
    # if yes, delete and recreate all messages to ensure ordering is correct
    prev_servers = set([(m.host, m.qport) for m in db.server_messages])
    new_servers = set([(s.host, s.qport) for s in config.servers])

    if prev_servers != new_servers:
        db.server_messages.clear()
        # delete all messages
        for m in db.server_messages:
            await m.delete(bot)

        # create new messages
        for server in config.servers:
            m = ServerMessage(server.host, server.qport, server.game_port, bot)
            await m.update(bot)
            db.server_messages.append(m)

        return

    # default case
    # update existing messages
    for m in db.server_messages:
        await m.update(bot)

    transaction.commit()


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
