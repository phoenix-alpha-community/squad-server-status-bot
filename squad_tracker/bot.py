#!/usr/bin/env python3

import asyncio
import config
import discord
import os.path
import pytz
import scheduling
import tk_listener
import traceback
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

    new_scheduler = not os.path.isfile(config.SCHEDULER_DB_FILENAME)
    scheduling.init_scheduler()

    # schedule tasks
    if new_scheduler:
        db.popper_job_ids.clear()
        for hour in config.SEEDING_PING_TIMES_HOURS_EST:
            id = scheduling.daily_execute(popper_ping, second=hour) # TODO hours
            db.popper_job_ids.append(id)
        scheduling.interval_execute(update_messages, [],
                                interval_seconds=config.UPDATE_INTERVAL_SECONDS)


async def update_messages():
    time = datetime.now(config.TIMEZONE)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} EST] Updating {config.SERVERS}")

    # check if the server set changed
    # if yes, delete and recreate all messages to ensure ordering is correct
    prev_servers = set([(m.host, m.qport) for m in db.server_messages])
    new_servers = set(config.SERVERS)

    if prev_servers != new_servers:
        db.server_messages.clear()
        # delete all messages
        for m in db.server_messages:
            await m.delete(bot)

        # create new messages
        for host, qport in config.SERVERS:
            m = ServerMessage(host, qport, bot)
            await m.update(bot)
            db.server_messages.append(m)

        return

    # default case
    # update existing messages
    for m in db.server_messages:
        await m.update(bot)


async def popper_ping():
    # get name of server that should be popped next
    next_server = None
    for m in db.server_messages:
        if m.playercount < config.POPPING_PLAYER_THRESHOLD:
            next_server = m.name
            break
    if next_server is None:
        return # no server needs popping

    await config.popper_channel.send(
        f"{config.popper_role.mention} **{next_server} is seeding and needs "
        f"your help!** "
        f"AFKs welcome and any help is appreciated!")


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
