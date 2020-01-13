from dataclasses import dataclass
from datetime import datetime

@dataclass
class TeamKill():
    time_utc : datetime
    victim : str
    killer : str
    weapon : str
    servername : str

