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


@bot.event
async def on_ready():
    config.init_config(bot)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    scheduling.init_scheduler()

    # schedule tasks
    scheduling.interval_execute(update_messages, [],
                            interval_seconds=config.UPDATE_INTERVAL_SECONDS)
    await update_messages()


async def update_messages():
    time = datetime.utcnow()
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str} UTC] Updating server messages")

    # Collect embeds
    embeds = []
    for server in config.servers:
        embeds.append(await get_server_embed(server))

    channel = config.server_channel

    # check if previous messages still exist
    # if one of them is missing, just delete the remaining ones
    wipe_messages = False
    for m_id in db.server_message_ids:
        try:
            message = await channel.fetch_message(m_id)
        except discord.errors.NotFound as e:
            wipe_messages = True
            break

    # if amount of messages doesn't match configured servers, delete them
    if len(db.server_message_ids) != len(config.servers):
        wipe_messages = True

    if wipe_messages:
        await channel.purge(limit=100,
                            check=lambda msg: msg.author == bot.user)
        db.server_message_ids.clear()

    # try to re-use old messages
    if len(db.server_message_ids) > 0:
        for m_id, embed in zip(db.server_message_ids, embeds):
            message = await channel.fetch_message(m_id)
            await message.edit(embed=embed)
    else: # otherwise, just create new ones
        for embed in embeds:
            message = await channel.send(embed=embed)
            db.server_message_ids.append(message.id)

    transaction.commit()


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
