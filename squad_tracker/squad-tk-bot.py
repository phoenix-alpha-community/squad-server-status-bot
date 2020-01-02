"""
  Created by Fear and Terror Python Team
            fearandterror.com
         discord.me/fearandterror
"""

import os  # used for follow()
import time  # used for follow()
import urllib3  # used for disc_post()
import json  # used for disc_post()
import re  # used for primary_parser()


class TKMonitor(object):
    def __init__(self, apihook, fname, tz, tzn, last=0, game_map=0, kills=[]):
        self.apihook = apihook
        self.fname = fname
        self.tz = tz
        self.tzn = tzn
        self.last = last
        self.game_map = game_map
        self.kills = kills

    ## Generate the lines in the text file as they are created
    def follow(self, fname):
        current = open(self.fname, "r", encoding="utf8")
        curino = os.fstat(current.fileno()).st_ino
        while True:
            while True:
                line = current.readline()
                if not line:
                    break
                yield line

            try:
                if os.stat(fname).st_ino != curino:
                    new = open(self.fname, "r", encoding="utf8")
                    current.close()
                    current = new
                    curino = os.fstat(current.fileno()).st_ino
                    continue
            except IOError:
                pass
            time.sleep(1)

    ## Parser to find teamkills, map, kill info
    def primary_parser(self, text):
        current_game_map = re.match(r"^\[.*\/Game\/Maps\/.*\/(?P<Map>(.*))\.+(persistent)?.*", text)

        if current_game_map != None:
            self.game_map = current_game_map.group("Map").split('.')[0]

        most_recent_kill = re.match(
            r"\[(?P<Year>[0-9]{4})\.(?P<Month>[0-9]{2})\.(?P<Day>[0-9]{2})\-(?P<Hour>[0-9]{2})\.(?P<Minute>([0-9].*))\..*\:.*\]\[(?P<LogID>([0-9]+))\]LogSquad: Player:(?P<Victim>(.*)) ActualDamage=.* from (?P<Killer>(.*)) caused by BP_(?P<Weapon>([^\_]*))\_.*$",
            text,
        )

        if most_recent_kill != None:
            self.kills.append(most_recent_kill)
            if len(self.kills) > 5:
                del self.kills[0]

        team_kill = re.match(
            r"^\[(?P<Year>[0-9]{4})\.(?P<Month>[0-9]{2})\.(?P<Day>[0-9]{2})\-(?P<Hour>[0-9]{2})\.(?P<Minute>[0-9].*)\]\[(?P<LogID>([0-9]+))\]LogSquadScorePoints: Verbose: ScorePointsDelayed: Points: -2.000000 ScoreEvent: TeamKilled (?P<Player>(.*))$",
            text,
        )

        if team_kill != None:
            for kill in self.kills:
                if kill.group("LogID") == team_kill.group("LogID"):
                    hour = int(kill.group("Hour")) - tz
                    if hour < 0:
                        hour += 24
                    match = {
                        "Date": f"{kill.group('Month')} {kill.group('Day')} {kill.group('Year')}",
                        "UTC": f"{kill.group('Hour')}:{kill.group('Minute')}",
                        tzn: f"{hour}:{kill.group('Minute')}",
                        "Killed": kill.group("Victim"),
                        "Killer": kill.group("Killer"),
                        "Weapon": kill.group("Weapon"),
                        "Map": self.game_map,
                    }  # create a dict with name:value
                    return match

    ## Posts the matched REGEX from primary_parser() to the discord channel specified in main()
    def disc_post(self, apihook, content):
        global last
        http = urllib3.PoolManager()
        data = {
            "username": "TK Bot",
            "avatar_url": "https://cdn.discordapp.com/attachments/608001303746183178/608480697799409664/TK_BOT.png",
            "content": "**Fear and Terror SQ Server 1 TK Tracker**",
            "embeds": [
                {
                    "fields": [
                        {"name": "**Date**", "value": content["Date"], "inline": True},
                        {"name": "**UTC**", "value": content["UTC"], "inline": True},
                        {
                            "name": f"**{tzn}**",
                            "value": content[f"{tzn}"],
                            "inline": True,
                        },
                        {
                            "name": "**Killer**",
                            "value": content["Killer"],
                            "inline": True,
                        },
                        {
                            "name": "**Victim**",
                            "value": content["Killed"],
                            "inline": True,
                        },
                        {
                            "name": "**Weapon**",
                            "value": content["Weapon"],
                            "inline": True,
                        },
                        {"name": "**Map**", "value": content["Map"], "inline": True},
                    ]
                }
            ],
        }  # data to pass in post request
        if self.last != content:  # varifies it's not posting the same BS over again
            encoded_data = json.dumps(data).encode("utf-8")
            http.request(
                "POST",
                apihook,
                body=encoded_data,
                headers={"Content-Type": "application/json"},
            )
            self.last = content


if __name__ == "__main__":
    apihook = "https://discordapp.com/api/webhooks/606277399780524052/MGvXkRUxMuI_FJ2jda5ytHiWZo7hkHG2GCDSLm9vLpy8M3_Tc2FxDpoQ-i3KZeDMeuti"  # discord API webhook  # discord API webhook
    fname = r"C:\servers\Squad_Server\SquadGame\Saved\Logs\SquadGame.log"  # squad log file
    if time.daylight == 0:
        tz = 5
        tzn = "EDT"
    else:
        tz = 4
        tzn = "EST"
    last = 0
    FaT = TKMonitor(apihook, fname, last, tz, tzn)
    for l in FaT.follow(fname):
        match = FaT.primary_parser(l)
        if match != None:
            FaT.disc_post(apihook, match)