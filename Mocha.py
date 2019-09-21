"""
Mocha - Discord bot for tracking Ko-fi supporters
by SockHungryClutz
Discord bot side handles initialization, handling messages to and from discord,
all the data associated with normal use, pretty much everything.
"""

VERSION = "0.0.1"

# TODO: create configuration file to store configurable settings like logging
# size and verbosity as well as in-server timing settings

# TODO: add the discord side of things and some bot commands / overrides

if __name__ == '__main__':
    print("Mocha : " + VERSION + "\nby SockHungryClutz\n(All further non-fatal messages will be output to logs)")
    
    # Start the logger
    logger = RollingLogger_Sync("MochaLog", 1048576‬, 5, 4)
    
    # TODO: create and spin-off process for listening to Ko-fi webhooks
    # TODO: initialize and run discord bot
