from dataclasses import dataclass

@dataclass
class TeamKill():
    timestamp_est : int
    victim : str
    killer : str
    weapon : str
    servername : str

