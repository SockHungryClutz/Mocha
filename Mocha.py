"""
Mocha - Discord bot for tracking Ko-fi supporters
by SockHungryClutz
Discord bot side handles initialization, handling messages to and from discord,
all the data associated with normal use, pretty much everything.
"""
import discord
from discord.ext import commands
from multiprocessing import Queue
from CSVParser import CSVParser
import asyncio
import configparser
import time
import datetime
import KofiListener

VERSION = "0.0.1"

bot = commands.Bot(command_prefix='m.',
        description="Hi! I'm Mocha V"+VERSION+"!\nUse \"m.<command>\""
                " to tell me to do something!",
        case_insensitive=True)

config = configparser.ConfigParser()
config.read("MochaConfig.ini")

# Format : [[discordIDs(int)],
#           [koFiName(str)],
#           [lastDonationTime(float)],
#           [totalDonated(float)],
#           [unconfirmedUsers(int)]] (last entry not same length as others)
userList = CSVParser.parseFile(config["mocha_config"]["user_file"])

koFiQueue = Queue()

# Async utility function to slide into them DM's
async def getDmChannel(usr):
    dm_chan = usr.dm_channel
    if dm_chan == None:
        await usr.create_dm()
        dm_chan = usr.dm_channel
    return dm_chan

# Async utility to convert user to member (there is a difference)
async def getMember(usr):
    guilds = await bot.fetch_guilds().flatten()
    for guild in guilds:
        mem = guild.get_member(usr.id)
        if mem != None:
            return mem
    return None

# Async utility to find a role by name
async def getRole(roleName):
    guilds = await bot.fetch_guilds().flatten()
    for guild in guilds:
        roles = guild.roles
        for rol in roles:
            if rol.name == roleName:
                return rol
    return None

# Sync utility to find a channel by name
def findChannel(chnl):
    foundChannel = None
    allChannels = bot.get_all_channels()
    for channel in allChannels:
        if channel.name == chnl:
            foundChannel = channel
    return foundChannel

# Sync utility to compare a timestamp to X days ago
def isOlderThan(timeStamp, daysAgo):
    thePast = time.mktime((datetime.date.today() -
                datetime.timedelta(days=daysAgo)).timetuple())
    return timeStamp < thePast

# Role check for commands
async def isAdmin(ctx):
    if ctx.author.top_role.permissions.manage_channels:
        return True
    else:
        return False

# Check to see any incoming messages from Ko-Fi
async def checkKoFiQueue():
    await bot.wait_until_ready()
    while not bot.is_closed():
        while not koFiQueue.empty():
            try:
                koFiData = koFiQueue.get()
                logger.info("Ko-Fi data received")
                # needs testing to ensure this timestamp format is correct
                jsonTime = koFiData["timestamp"]
                jsonTime = jsonTime.split('.')[0]
                koFiTime = time.mktime(datetime.datetime.strptime(
                        jsonTime, "%Y-%m-%dT%H:%M:%S").timetuple())
                koFiUser = koFiData["from_name"]
                koFiAmount = float(koFiData["amount"])
                if koFiUser in userList[1]:
                    # Existing user, update last donation time and total donated
                    idx = userList[1].index(koFiUser)
                    userList[2][idx] = str(koFiTime)
                    userList[3][idx] = str(koFiAmount + float(userList[3][idx]))
                    if userList[0][idx] != '0':
                        mem = await getMember(bot.get_user(int(userList[0][idx])))
                        warnRole = await getRole(config["mocha_config"]["warning_role"])
                        try:
                            await mem.remove_roles(warnRole, reason=userList[1][idx]+
                                    " has made a payment")
                        except BaseException as e:
                            pass
                else:
                    # New user, add to userList
                    userList[0].append('0')
                    userList[1].append(koFiUser)
                    userList[2].append(str(koFiTime))
                    userList[3].append(str(koFiAmount))
                CSVParser.writeNestedList(config["mocha_config"]["user_file"],
                        userList, 'w')
            except BaseException as e:
                logger.warning("Error parsing KoFi data\nOriginal Data:\n" +
                        str(koFiData) + "\nError Details:\n" +
                        str(e))
        await asyncio.sleep(int(config["mocha_config"]["kofi_check_delay"]))

# Check for users who are late on payments, deal with them accordingly
async def checkPaymentTime():
    await bot.wait_until_ready()
    while not bot.is_closed():
        gracePeriod = 32 + int(config["mocha_config"]["grace_period"])
        idx = 0
        while idx < len(userList[0]):
            if int(userList[0][idx]) == 0:
                continue
            if isOlderThan(float(userList[2][idx]), 32):
                usr = bot.get_user(int(userList[0][idx]))
                mem = await getMember(usr)
                msgChannel = await getDmChannel(usr)
                if msgChannel == None:
                    continue
                if isOlderThan(float(userList[2][idx]), gracePeriod):
                    await msgChannel.send(config["message_strings"]["kick_message"])
                    await mem.kick(reason=userList[1][idx]+
                            " is no longer a Ko-fi supporter")
                else:
                    await msgChannel.send(config["message_strings"]["warning_message"])
                    warnRole = await getRole(config["mocha_config"]["warning_role"])
                    await mem.add_roles(warnRole, reason=userList[1][idx]+
                            " has missed a monthly payment")
            idx += 1
        await asyncio.sleep(int(config["mocha_config"]["payment_check_delay"]))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with a cup of Ko-fi", type=1))
    logger.info('Discord log in success!')

# Send welcome message on member join
@bot.event
async def on_member_join(member):
    welcomeChannel = findChannel(config["mocha_config"]["welcome_channel"])
    userList[4].append(str(member.id))
    CSVParser.writeNestedList(config["mocha_config"]["user_file"], userList, 'w')
    if welcomeChannel != None:
        await welcomeChannel.send(config["message_strings"]["welcome_message"])

# Handle member leaving
@bot.event
async def on_member_remove(member):
    if str(member.id) in userList[0]:
        idx = userList[0].index(str(member.id))
        userList[0][idx] = '0'
    if str(member.id) in userList[4]:
        idx = userList[4].index(str(member.id))
        userList[4][idx] = '0'
    CSVParser.writeNestedList(config["mocha_config"]["user_file"], userList, 'w')

# Confirming new users through on_message hook
@bot.event
async def on_message(message):
    welcomeChannel = findChannel(config["mocha_config"]["welcome_channel"])
    # Confirm this is in the welcome channel, by an unconfirmed user, has only
    # one word, is a ko-fi supporter, and is unattached to a Discord id
    if message.channel.id == welcomeChannel.id:
        if str(message.author.id) in userList[4]:
            if not ' ' in message.content:
                if message.content in userList[1]:
                    idx = userList[1].index(message.content)
                    if userList[0][idx] == '0':
                        if isOlderThan(float(userList[2][idx]), 32):
                            return await welcomeChannel.send("Sorry, " + message.content +
                                    " has not made any recent Ko-fi donations!"
                        userList[0][idx] = str(message.author.id)
                        CSVParser.writeNestedList(config["mocha_config"]["user_file"],
                                userList, 'w')
                        newRole = await getRole(config["mocha_config"]["supporter_role"])
                        await message.author.add_roles(newRole)
                        await welcomeChannel.send(config["message_strings"]["accept_message"])
                    else:
                        await welcomeChannel.send("Sorry, looks like that Ko-fi"
                                " user is already on this server!")
                else:
                    await welcomeChannel.send("Sorry, " + message.content +
                            " has not made any recent Ko-fi donations!"
    await bot.process_commands(message)

# Overwrite default help command to make it less generic
@bot.remove_command("help")

@bot.command()
async def help(ctx):
    await ctx.send("Hi! I'm Mocha V"+VERSION+"! A bot that keeps track of Ko-fi" +
            " payments and helps manage this Ko-fi exclusive Discord guild!\n" +
            "Unfortunately I don't have any commands for normal users (other" +
            " than this), sorry!")

# Get the user list as a CSV for mods
@bot.command(hidden=True)
@commands.check(is_admin)
async def getMembers(ctx):
    """Return a CSV of info about members"""
    # Although data processing/searching is easier the way userList is,
    # the CSV file output looks better rotated 90 degrees (rows become columns)
    finalCSV = [[] for _ in xrange(len(userList) + 1)]
    finalCSV[idx+1].append("Discord ID")
    finalCSV[idx+1].append("Ko-fi Username")
    finalCSV[idx+1].append("Last Donation Timestamp")
    finalCSV[idx+1].append("Total Donated")
    for idx in range(0, len(userList[0])):
        finalCSV[idx+1].append(userList[0][idx])
        finalCSV[idx+1].append(userList[1][idx])
        finalCSV[idx+1].append(userList[2][idx])
        finalCSV[idx+1].append(userList[3][idx])
    CSVParser.writeNestedList("tempMemberList.csv", finalCSV, 'w')
    listFiles = [
        discord.File("tempMemberList.csv", "MemberList.csv"),
    ]
    dmChannel = await getDmChannel(ctx.author)
    if dmChannel != None:
        await dmChannel.send("Here's all info on every supporter for ya!", files=listFiles)

# Reload the configuration file
@bot.command(hidden=True)
@commands.check(is_admin)
async def reloadConfig(ctx):
    """Reload the configuration file"""
    global config
    config = configparser.ConfigParser()
    config.read("MochaConfig.ini")
    await ctx.send("Done!")

if __name__ == '__main__':
    print("Mocha : " + VERSION + "\nby SockHungryClutz\n(All further non-fatal"
            "messages will be output to logs)")
    
    # Start the logger
    logger = RollingLogger_Sync(
        config["logging"]["discord_log_name"],
        config["logging"]["max_log_size"],
        config["logging"]["max_number_logs"],
        config["logging"]["log_verbosity"]))
    
    p = Process(target=initListener, args=(koFiQueue,))
    p.start()
    
    theLoop = bot.loop
    theLoop.create_task(checkKoFiQueue())
    theLoop.create_task(checkPaymentTime())
    while True:
        if bot.is_closed():
            logger.warning("Bot closed, attempting reconnect...")
            bot.clear()
        try:
            theLoop.run_until_complete(bot.start(
                    config["mocha_config"]["token"]))
        except BaseException as e:
            logger.warning("Discord connection reset:\n" + str(e))
        finally:
            time.sleep(60)
    theLoop.close()
