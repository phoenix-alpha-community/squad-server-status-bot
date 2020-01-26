import asyncio
import config
import jsonpickle
import logging
import msvcrt
import os
import re
import sys
import urllib3
import win32file
from datetime import datetime
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
from pytz import timezone
from teamkill import TeamKill
from tzlocal import get_localzone

mqtt_client = None

class TKMonitor():

    def __init__(self, host, qport, basedir):
        self.basedir = basedir
        self.log_filename = basedir + r"\SquadGame\Saved\Logs\SquadGame.log"
        self.admincam_log_filename = basedir + r"\SquadGame\Saved\Logs\admincam.log"
        self.recent_damages = []
        self.seen_tks = set()
        self.last_log_id = 0
        self.server_host = host
        self.server_qport = qport
        self.active_admin_cam_users = set()


    def _open_log_file(self):
        # source:
        # https://www.thepythoncorner.com/2016/10/python-how-to-open-a-file-on-windows-without-locking-it/
        # get an handle using win32 API, specifying the SHARED access!
        handle = win32file.CreateFile(self.log_filename,
                                        win32file.GENERIC_READ,
                                        win32file.FILE_SHARE_DELETE |
                                        win32file.FILE_SHARE_READ |
                                        win32file.FILE_SHARE_WRITE,
                                        None,
                                        win32file.OPEN_EXISTING,
                                        0,
                                        None)
        # detach the handle
        detached_handle = handle.Detach()
        # get a file descriptor associated to the handle
        file_descriptor = msvcrt.open_osfhandle(
            detached_handle, os.O_RDONLY)
        # open the file descriptor
        f = open(file_descriptor, encoding="UTF-8")
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
                try:
                    line = f.readline()
                except UnicodeDecodeError as e:
                    sys.stderr.write("[WARN] Skipped line because of decode error")
                    line = "DECODE_ERROR"
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

    ## Parser to find teamkills, map, kill info
    def parse_line(self, line):
        '''Returns TK object if TK occurred, `None` otherwise.'''

        # try matching to admin cam usage format
        if self._match_admincam(line):
            return None

        # try matching to damage format
        if self._match_damage(line):
            return None

        # try matching to teamkill format
        return self._match_teamkill(line)

    def _match_damage(self, line):
        '''Returns `True` if line was a damage notification,
        `False` otherwise.'''

        actual_damage = re.search(
            r"\[(?P<time>[^\]]+)\]" # time
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"LogSquad: Player:"
            r"(?P<victim>.*)" # victim
            r" ActualDamage=.* from "
            r"(?P<killer>.*)" # killer
            r" caused by "
            r"BP_(?P<weapon>[^\_]*)\_", # weapon
            line,
        )

        # remember damage
        if actual_damage == None:
            return False

        self.recent_damages.append(actual_damage)
        # only track the last 20 damages
        if len(self.recent_damages) > 20:
            del self.recent_damages[0]
        return True # matched

    def _match_teamkill(self, line):
        '''Returns TK object if TK occurred, `None` otherwise.'''

        team_kill = re.search(
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"[^\n]*"
            r"LogSquadScorePoints:[^\n]*TeamKilled",
            line,
        )

        if team_kill == None:
            return None

        # delete duplicate info on log id wrap-around
        if int(team_kill.group("log_id")) + 500 < self.last_log_id:
            self.seen_tks.clear()
        self.last_log_id = int(team_kill.group("log_id"))

        # check for duplicate
        if team_kill.group("log_id") in self.seen_tks:
            return None

        # match log IDs
        for dmg in self.recent_damages:
            if dmg.group("log_id") == team_kill.group("log_id"):
                time_str = dmg.group("time")
                time_naive = datetime.strptime(time_str, "%Y.%m.%d-%H.%M.%S:%f")
                # Timestamps are UTC
                time_utc = timezone("UTC").localize(time_naive)
                victim = dmg.group("victim")
                killer = dmg.group("killer")
                weapon = dmg.group("weapon")
                tk = TeamKill(time_utc, victim, killer, weapon,
                              self.server_host, self.server_qport)

                # remember log ID of last TK to avoid duplicates
                self.seen_tks.add(team_kill.group("log_id"))

                return tk

    def _match_admincam(self, line):
        '''Returns `True` if line was admin cam usage,
        `False` otherwise.'''

        change = None

        # check for possess
        match = re.search(
            r"\[(?P<time>[^\]]+)\]" # time
            r"\[(?P<log_id>[0-9]+)\]" # log_id
            r"[^\n]*"
            r"ASQPlayerController::Possess"
            r"[^\n]*"
            r"PC=(?P<user>.*) " # user
            r"[^\n]*"
            r"Pawn=CameraMan_C_" # admin cam
            ,
            line,
        )

        if match != None:
            change = "++++++++++++ ENTER"
            user = match.group("user")
            self.active_admin_cam_users.add(user)
        else:
            # check for unpossess
            match = re.search(
                r"\[(?P<time>[^\]]+)\]" # time
                r"\[(?P<log_id>[0-9]+)\]" # log_id
                r"[^\n]*"
                r"ASQPlayerController::UnPossess"
                r"[^\n]*"
                r"PC=(?P<user>.*)" # user
                ,
                line,
            )

            if match != None:
                change = "--- POSSIBLE LEAVE"
                user = match.group("user")
                if user not in self.active_admin_cam_users:
                    # false positive
                    return False
                else:
                    self.active_admin_cam_users.remove(user)

        if change is None:
            return False

        time_str = match.group("time")
        time_naive = datetime.strptime(time_str, "%Y.%m.%d-%H.%M.%S:%f")
        # Timestamps are UTC
        time_utc = timezone("UTC").localize(time_naive)
        time_est = time_utc.astimezone(config.TIMEZONE)
        time_str_est = time_est.strftime("%Y.%m.%d - %H:%M:%S")
        user = match.group("user")
        log_message = f"[{time_str_est} EST] {change}: {user}"

        with open(self.admincam_log_filename, "a") as f:
            f.write(log_message + "\n")
        print(f"[ADMIN CAM][{self.server_qport}]{log_message}")

        return True


    async def tk_follow(self):
        async for line in self._log_follow():
            tk = self.parse_line(line)
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


async def run_tkm(host, qport, basedir):
    tkm = TKMonitor(host, qport, basedir)
    async for tk in tkm.tk_follow():
        payload = jsonpickle.dumps(tk).encode("UTF-8")
        print(f"[SEND] {tk}")
        await mqtt_client.publish(config.MQTT_TOPIC, payload, qos=QOS_2)


async def main():
    await init_mqtt()
    tasks = []
    for server in config.servers:
        tasks.append(asyncio.create_task(
            run_tkm(server.host, server.qport, server.base_dir)))

    for t in tasks:
        await t


if __name__ == "__main__":
    asyncio.run(main())
