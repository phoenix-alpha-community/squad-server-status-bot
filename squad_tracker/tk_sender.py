import asyncio
import config
import json
import logging
import os
import re
import urllib3
from dataclass import dataclass
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2

mqtt_client = None

@dataclass
class TeamKill():
    time : datetime
    victim : str
    killer : str
    weapon : str

class TKMonitor():

    def __init__(self, basedir):
        self.basedir = basedir
        self.log_filename = basedir + "\SquadGame\Saved\Logs\SquadGame.log"
        self.config_filename = basedir + "\SquadGame\ServerConfig\Server.cfg"
        self.recent_damages = []


    def _open_log_file(self):
        f = open(self.logfile, "r", encoding="utf8")
        # seek to end
        config_file.seek(0, os.SEEK_END)
        file_id = os.fstat(f.fileno()).st_ino

        return (f, file_id)

    ## Generate the lines in the text file as they are created
    def follow(self):
        f, file_id = self._open_log_file()

        # read indefinitely
        while True:
            # read until end of file
            while True:
                line = current.readline()
                if not line:
                    break
                yield line

            try:
                # check if file has been replaced
                if os.stat(fname).st_ino != file_id:
                    # close and re-open
                    f.close()
                    f, file_id = self._open_log_file()
            except IOError:
                pass
            asyncio.sleep(1)

    ## Parser to find teamkills, map, kill info
    def parse_line(self, line):

        # try matching log line to damage format
        actual_damage = re.match(
            r"\[(?P<time>[^\]]+)\]" # time
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"LogSquad: Player:"
            r"(?P<victim>.*)" # victim
            r"ActualDamage=.* from "
            r"(?P<killer>.*)" # killer
            r"caused by "
            r"BP_(?P<weapon>[^\_]*)\_", # weapon
            text,
        )

        # remember damage
        if actual_damage != None:
            self.recent_damages.append(actual_damage)
            # only track the last 20 damages
            if len(self.recent_damages) > 20:
                del self.recent_damages[0]
            return None

        # try matching log line to teamkillformat
        team_kill = re.match(
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"LogSquadScorePoints:[^\n]*TeamKilled"
            text,
        )

        if team_kill == None:
            return None

        # match log IDs
        for kill in self.kills:
            if kill.group("log_id") == team_kill.group("log_id"):
                time_str = kill.group("time")
                time = datetime.strptime(time_str, "%Y.%m.%d-%H.%M.%S:%f")
                victim = kill.group("victim")
                killer = kill.group("killer")
                weapon = kill.group("weapon")

                tk = TeamKill(time, victim, killer, weapon)
                return tk


async def init_mqtt():
    '''Must be called after config is initialized.'''
    global mqtt_client
    mqtt_client = MQTTClient()

    user = config.MQTT_PUB_USER
    password = config.MQTT_PUB_PASSWORD
    host, port = config.MQTT_ADDRESS
    url = f"mqtt://{user}:{password}@{host}:{port}/"
    print("preconnect")
    await mqtt_client.connect(url)
    print("connected")

async def run_tkm(basedir):
    tkm = TKMonitor(basedir)
    for line in tkm.follow():
        tk = tlm.primary_parser(line)
        if tk != None:
            payload = json.dumps(tk).encode("UTF-8")
            await mqtt_client.publish(config.MQTT_TOPIC, payload, qos=QOS_2)

if __name__ == "__main__":
    for basedir in config.SERVER_BASE_DIRS:
        asyncio.ensure_future(run_tkm(basedir))
