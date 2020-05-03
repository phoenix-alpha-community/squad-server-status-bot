#!/usr/bin/env python3

import asyncio
import config
import discord
import scheduling
import traceback
import transaction
from BTrees.OOBTree import TreeSet
from database import db
from datetime import datetime
from discord.ext import commands
from server_message import get_server_embed

bot = commands.Bot(command_prefix=config.BOT_CMD_PREFIX)
scheduler_initialized = False


@bot.event
async def on_ready():
    config.init_config(bot)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    scheduling.init_scheduler()

    # Schedule tasks
    # Since on_ready may run multiple times due to reconnects, we need to make
    # sure we only schedule jobs once
    global scheduler_initialized
    if not scheduler_initialized:
        scheduler_initialized = True
        scheduling.interval_execute(update_squad_messages, [],
                                    interval_seconds=config.UPDATE_INTERVAL_SECONDS)
        scheduling.interval_execute(post_update_messages, [],
                                    interval_seconds=config.UPDATE_INTERVAL_SECONDS)
        await update_squad_messages()
        await update_post_messages()


async def update_squad_messages():
    time = datetime.utcnow()
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} UTC] Updating server messages")

    # Collect embeds
    embeds = []
    for server in config.squadservers:
        embeds.append(await get_server_embed(server))

    channel = config.squad_server_channel

    # check if previous messages still exist
    # if one of them is missing, just delete the remaining ones
    wipe_messages = False
    for m_id in db.squad_server_message_ids:
        try:
            message = await channel.fetch_message(m_id)
        except discord.errors.NotFound as e:
            wipe_messages = True
            break

    # if amount of messages doesn't match configured servers, delete them
    if len(db.squad_server_message_ids) != len(config.squadservers):
        wipe_messages = True

    if wipe_messages:
        await channel.purge(limit=100,
                            check=lambda msg: msg.author == bot.user)
        db.squad_server_message_ids.clear()

    # try to re-use old messages
    if len(db.squad_server_message_ids) > 0:
        for m_id, embed in zip(db.squad_server_message_ids, embeds):
            message = await channel.fetch_message(m_id)
            await message.edit(embed=embed)
    else: # otherwise, just create new ones
        for embed in embeds:
            message = await channel.send(embed=embed)
            db.squad_server_message_ids.append(message.id)

    transaction.commit()


async def update_post_messages():
    time = datetime.utcnow()
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} UTC] Updating server messages")

    # Collect embeds
    embeds = []
    for server in config.postservers:
        embeds.append(await get_server_embed(server))

    channel = config.post_server_channel

    # check if previous messages still exist
    # if one of them is missing, just delete the remaining ones
    wipe_messages = False
    for m_id in db.post_server_message_ids:
        try:
            message = await channel.fetch_message(m_id)
        except discord.errors.NotFound as e:
            wipe_messages = True
            break

    # if amount of messages doesn't match configured servers, delete them
    if len(db.post_server_message_ids) != len(config.postservers):
        wipe_messages = True

    if wipe_messages:
        await channel.purge(limit=100,
                            check=lambda msg: msg.author == bot.user)
        db.post_server_message_ids.clear()

    # try to re-use old messages
    if len(db.post_server_message_ids) > 0:
        for m_id, embed in zip(db.post_server_message_ids, embeds):
            message = await channel.fetch_message(m_id)
            await message.edit(embed=embed)
    else: # otherwise, just create new ones
        for embed in embeds:
            message = await channel.send(embed=embed)
            db.post_server_message_ids.append(message.id)

    transaction.commit()

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
