import asyncio
import config
import traceback
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

async def listener(client):
    while True:
        try:
            message = await client.deliver_message()
            packet = message.publish_packet
            assert packet.variable_header.topic_name == config.MQTT_TOPIC
            data = packet.payload.data.decode("UTF-8")
            print(f"[MQTT] {data}")
        except Exception as e:
            traceback.print_exception(e)


async def init_tk_listener():
    '''Must be called after config is initialized.'''
    client = MQTTClient()

    user = config.MQTT_SUB_USER
    password = config.MQTT_SUB_PASSWORD
    host, port = config.MQTT_ADDRESS
    url = f"mqtt://{user}:{password}@{host}:{port}/"
    print("preconnect")
    await client.connect(url)
    print("connected")
    await client.subscribe([(config.MQTT_TOPIC, QOS_2)])
    print("subscribed")
    asyncio.ensure_future(listener(client))
