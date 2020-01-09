#!/usr/bin/env python3

import asyncio
import config
import discord
import os.path
import scheduling
import traceback
import pytz
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
    new_scheduler = not os.path.isfile(config.SCHEDULER_DB_FILENAME)
    scheduling.init_scheduler()

    # schedule tasks
    if new_scheduler:
        db.popper_job_ids.clear()
        for hour in config.SEEDING_PING_TIMES_HOURS_EST:
            id = scheduling.daily_execute(popper_ping, second=hour)
            db.popper_job_ids.append(id)
        scheduling.interval_execute(update_messages, [],
                                interval_seconds=config.UPDATE_INTERVAL_SECONDS)


async def update_messages():
    time = datetime.now(config.TIMEZONE)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} EST] Updating {config.SERVERS}")

    server_messages = set(db.server_messages)

    # delete unwanted messages
    deleted_messages = set()
    for m in server_messages:
        if (m.host, m.qport) not in config.SERVERS:
           await m.delete(bot)
           deleted_messages.add(m)
    server_messages -= deleted_messages

    # update existing messages
    updated_ports = set()
    for m in server_messages:
        await m.update(bot)
        updated_ports.add(m.qport)

    # create new messages
    for host, qport in config.SERVERS:
        if qport not in updated_ports:
            m = ServerMessage(host, qport, bot)
            await m.update(bot)
            server_messages.add(m)

    db.server_messages = TreeSet()
    for x in server_messages:
        db.server_messages.add(x)


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
