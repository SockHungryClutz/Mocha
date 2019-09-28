# Mocha  
Discord bot for tracking Ko-fi supporters

-----

## Requirements

* [Python 3](https://www.python.org/downloads/)  
* [pip](https://pypi.org/project/pip/)

After installing the above, clone this repo and run `pip install -r requirements.txt` inside the cloned repo.

-----

## Setup

Follow [these steps](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) to set up a discord bot. Set up the requirements as outlined in the **Requirements** section. Open `MochaConfig.ini` and fill in the values as you see fit. Make sure the bot has the following permissions:

- Send messages  
- Read message history  
- Manage roles  
- Kick members  

-----

## Usage

Open a command window / powershell / terminal and enter `python3 Mocha.py`

To run this completely headless, use `nohup python3 Mocha.py & disown` in a \*nix environment

-----

## Other Stuff

You can modify the configuration while the bot is running, then send the command `m.reloadConfig` in discord to make changes to the discord configuration  
(The process for listening for Ko-fi webhooks will not reload the config, changing the configuration of this requires stopping and restarting Mocha)

To stop Mocha:  
`killall python3`
