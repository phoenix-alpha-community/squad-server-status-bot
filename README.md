# Squad Tracker Bot
A Discord bot for the Fear and Terror Discord that tracks the current status of
the Fear and Terror Squad servers.

## Overview
- **Server status message**.
The bot will post and update status messages in regular intervals in a
configurable channel for a configurable set of servers.

![Image](images/server-status.png)

## Installation
1. Clone this repository
2. Install dependencies via `pip`:
    - Linux: `pip install -r requirements.txt`
    - Windows: `python3.exe -m pip install -r requirements.txt`
      (You might have to navigate to wherever your python installation is)
3. In the `squad_server_status_bot` directory, make a copy of
   `config-sample.py` called `config.py`
4. Change the config parameters.
   The default parameters are set up to match the Fear and Terror Discord and
   Squad servers.
   Settings that still need to be changed:
    - `BOT_TOKEN`: Discord Bot authentication token
