import asyncio
import config
import discord
import jsonpickle
import traceback
import sys
from database import db
from datetime import datetime
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from pytz import timezone
from teamkill import TeamKill

async def listener(client):
    while True:
        # keep loop alive
        try:
            message = await client.deliver_message()
            packet = message.publish_packet
            assert packet.variable_header.topic_name == config.MQTT_TOPIC
            data = packet.payload.data.decode("UTF-8")
            tk = jsonpickle.loads(data)
            await log_tk(tk)
        except Exception as e:
            traceback.print_exc(e)

async def log_tk(tk : TeamKill):
    # Create embed
    embed = discord.Embed(title=f"TK on {tk.servername}")

    # Time (EST)
    time_utc = tk.time_utc
    time_est = time_utc.astimezone(config.TIMEZONE)
    time_est_str = time_est.strftime("%m/%d/%Y %H:%M:%S")
    embed.add_field(name='Date / Time (EST)', value=time_est_str, inline=True)

    # Time (UTC)
    time_utc_str = time_utc.strftime("%H:%M:%S")
    if time_utc.date() > time_est.date():
        time_utc_str += " (+1 day)"
    embed.add_field(name='Time (UTC)', value=time_utc_str, inline=True)

    # Get map from cached server message
    cur_map = "Unknown"
    for m in db.server_messages:
        if m.name == tk.servername:
            cur_map = m.cur_map
    embed.add_field(name='Map', value=cur_map, inline=True)

    # Killer
    embed.add_field(name='Killer', value=tk.killer, inline=True)
    # Victim
    embed.add_field(name='Victim', value=tk.victim, inline=True)
    # Weapon
    embed.add_field(name='Weapon', value=tk.weapon, inline=True)


    await config.tk_channel.send(embed=embed)


async def init_tk_listener():
    '''Must be called after config is initialized.'''
    client = MQTTClient()

    user = config.MQTT_SUB_USER
    password = config.MQTT_SUB_PASSWORD
    host, port = config.MQTT_ADDRESS
    url = f"mqtt://{user}:{password}@{host}:{port}/"
    print("MQTT connecting...")
    await client.connect(url)
    await client.subscribe([(config.MQTT_TOPIC, QOS_2)])
    print("MQTT connected!")
    asyncio.ensure_future(listener(client))
