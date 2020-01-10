import asyncio
import config
import jsonpickle
import logging
import os
import re
import urllib3
from datetime import datetime
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from teamkill import TeamKill
from tzlocal import get_localzone

mqtt_client = None

class TKMonitor():

    def __init__(self, basedir):
        self.basedir = basedir
        self.log_filename = basedir + "\SquadGame\Saved\Logs\SquadGame.log"
        self.config_filename = basedir + "\SquadGame\ServerConfig\Server.cfg"
        self.recent_damages = []


    def _open_log_file(self):
        f = open(self.log_filename, "r", encoding="utf8")
        # seek to end
        f.seek(0, os.SEEK_END)
        file_id = os.fstat(f.fileno()).st_ino

        return (f, file_id)

    ## Generate the lines in the text file as they are created
    async def _log_follow(self):
        f, file_id = self._open_log_file()
        # read indefinitely
        while True:
            # read until end of file
            while True:
                line = f.readline()
                if not line:
                    break
                yield line
            try:
                # check if file has been replaced
                if os.stat(self.log_filename).st_ino != file_id:
                    # close and re-open
                    f.close()
                    f, file_id = self._open_log_file()
            except IOError:
                pass
            await asyncio.sleep(1)

    def _get_servername(self):
        with open(self.config_filename, "r") as config_file:
            for line in config_file:
                if not line.startswith("ServerName="):
                    continue
                _, name = line.split("=")
                name = name.replace("\"", "")
                return name

    ## Parser to find teamkills, map, kill info
    def parse_line(self, line):

        # try matching log line to damage format
        actual_damage = re.search(
            r"\[(?P<time>[^\]]+)\]" # time
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"LogSquad: Player:"
            r"(?P<victim>.*)" # victim
            r"ActualDamage=.* from "
            r"(?P<killer>.*)" # killer
            r"caused by "
            r"BP_(?P<weapon>[^\_]*)\_", # weapon
            line,
        )

        # remember damage
        if actual_damage != None:
            self.recent_damages.append(actual_damage)
            # only track the last 20 damages
            if len(self.recent_damages) > 20:
                del self.recent_damages[0]
            return None

        # try matching log line to teamkillformat
        team_kill = re.search(
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"[^\n]*"
            r"LogSquadScorePoints:[^\n]*TeamKilled",
            line,
        )

        if team_kill == None:
            return None

        # match log IDs
        for dmg in self.recent_damages:
            if dmg.group("log_id") == team_kill.group("log_id"):
                time_str = dmg.group("time")
                time_naive = datetime.strptime(time_str, "%Y.%m.%d-%H.%M.%S:%f")
                time_local = get_localzone().localize(time_naive)
                time_est = time_local.astimezone(config.TIMEZONE)
                timestamp_est = time_est.timestamp()
                victim = dmg.group("victim")
                killer = dmg.group("killer")
                weapon = dmg.group("weapon")
                servername = self._get_servername()
                tk = TeamKill(timestamp_est, victim, killer, weapon, servername)
                return tk

    async def tk_follow(self):
        async for line in tkm.follow():
            tk = tkm.parse_line(line)
            if tk != None:
                yield tk


async def init_mqtt():
    '''Must be called after config is initialized.'''
    global mqtt_client
    mqtt_client = MQTTClient()

    user = config.MQTT_PUB_USER
    password = config.MQTT_PUB_PASSWORD
    host, port = config.MQTT_ADDRESS
    url = f"mqtt://{user}:{password}@{host}:{port}/"
    print("MQTT connecting...")
    await mqtt_client.connect(url)
    print("MQTT connected!")


async def run_tkm(basedir):
    tkm = TKMonitor(basedir)
    async for tk in tkm.tk_follow():
        payload = jsonpickle.dumps(tk).encode("UTF-8")
        print(f"[SEND] {payload})
        await mqtt_client.publish(config.MQTT_TOPIC, payload, qos=QOS_2)


async def main():
    await init_mqtt()
    tasks = []
    for basedir in config.SERVER_BASE_DIRS:
        tasks.append(asyncio.create_task(run_tkm(basedir)))

    for t in tasks:
        await t


if __name__ == "__main__":
    asyncio.run(main())
