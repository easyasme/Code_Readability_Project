#Version: 0.1

"""
TODO: Check for possible performance optimization, reduce redundancy
TODO: Add localization
TODO: Create some sort of interface for customization for each server, web interface?
"""

import discord
import os
import time
import asyncio
import sqlite3
import sys
import datetime
import logging
import traceback
from pathlib import Path
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions, NotOwner

# This section of code is responsible for setting up logging for the bot.
logname = Path(sys.path[0], 'bot.log')

logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s.%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

locales = ('en-US', 'de')
owners = [459747395027075095]

logger = logging.getLogger()

def is_authorized(**perms):
    original = commands.has_permissions(**perms).predicate
    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return ctx.author.id in owners or await original(ctx)
    return commands.check(extended_check)

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# The `StartupTimes` class provides methods for initializing, retrieving, updating, and clearing
# startup times stored in a SQLite database.
class StartupTimes:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_startup()

    def init_startup(self):
        """
        The function initializes a SQLite database table for storing startup times if it doesn't already
        exist.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS startup_times
                        (startup_time REAL)''')
            con.commit()

    def retrieve_startup_times(self):
        """
        The function retrieves the startup times from a SQLite database.
        :return: a list of startup times retrieved from the "startup_times" table in the SQLite
        database.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('SELECT startup_time FROM startup_times')
            return [row[0] for row in c.fetchall()]
        
    def update_startup_times(self, new_time):
        """
        The function updates the startup times in a SQLite database with a new time value.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('INSERT INTO startup_times (startup_time) VALUES (?)', (new_time,))
            con.commit()

    def clear_startup_times(self):
        """
        The function clears all the startup times stored in a SQLite database.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('DELETE FROM startup_times')
            con.commit()

# The `Settings` class is a Python class that manages settings stored in a SQLite database.
class Settings:
    def __init__(self):
        """
        The function initializes the class instance with the necessary attributes.
        """
        self.db_path = Path(sys.path[0], 'bot.db')
        self.init_settings()
        self.bottoken = self.retrieve_setting(setting='bottoken')
        self.statuschannel_id = self.retrieve_setting(setting='statuschannel_id')
        self.bot_status = self.retrieve_setting(setting='bot_status')

    def init_settings(self):
        """
        The function initializes settings in a SQLite database, prompts the user for input if the
        settings are missing or invalid, and updates the settings accordingly.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            settings = ['bottoken', 'statuschannel_id', 'bot_status']
            setup_vars = ['bottoken', 'statuschannel_id', 'bot_status']
            default_settings = ['Invalid', 'Invalid', 'Custom Bot status']
            c.execute('CREATE TABLE IF NOT EXISTS settings(setting TEXT, value TEXT)')
            con.commit()
            for s in settings:
                if not self.check_setting(s):
                    c.execute('INSERT INTO settings (setting) VALUES (?)', (s,))
                    con.commit()
        for i, s in enumerate(setup_vars):
            while True:
                if not self.check_setting(s) or self.retrieve_setting(s) is None:
                    val = input(f'{s}:')
                    if val == '':
                        if default_settings[i] == 'Invalid':
                            continue
                        val = default_settings[i]
                    self.update_settings(val, s)
                    print(f'Added {s}: {val}\n')
                break     
    
    def check_setting(self, setting: str) -> bool:
        """
        The function checks if a given setting exists in a SQLite database table and returns a boolean
        value indicating its presence.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('SELECT * FROM settings WHERE setting =?', (setting,))
            result = c.fetchone()
            return result is not None and result[0] is not None

    def retrieve_setting(self, setting: str) -> str:
        """
        The function retrieves the value of a specific setting from a SQLite database.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            c.execute('SELECT value FROM settings WHERE setting =?', (setting,))
            return c.fetchone()[0]
    
    def update_settings(self, value: str, setting: str):
        """
        The function updates a setting in a SQLite database with a given value.
        """
        with sqlite3.connect(self.db_path) as con:
            c = con.cursor()
            if not self.check_setting(setting):
                c.execute('INSERT INTO settings (setting, value) VALUES (?, ?)', (setting, value))
            else:
                c.execute('UPDATE settings SET value = ? WHERE setting = ?', (value, setting))
            con.commit()

# The `MyView` class is a Discord UI view that contains two buttons, one for killing the bot and one
# for restarting it, both of which require the owner's permission.
class MyView(discord.ui.View):
    @discord.ui.button(label="Killbot", style=discord.ButtonStyle.danger)
    @commands.is_owner()
    async def button_callbackkillbot(self, button, interaction):
        try:
            await interaction.response.defer()
            logger.info("Bot Closed")
            await bot.close()
            sys.exit(1)
        except:logger.error(traceback.format_exc())
    @discord.ui.button(label="Restart", style=discord.ButtonStyle.danger)
    @commands.is_owner()
    async def button_callbackrestart(self, button: discord.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            logger.info('Restarting')
            await restart()
        except:logger.error(traceback.format_exc())
    @discord.ui.button(label="Sync Commands", row=1)
    @commands.is_owner()
    async def button_callbacksync(self, button: discord.Button, interaction: discord.Interaction):
        try:
            await interaction.response.send_message('Syncing Commands', ephemeral=True, delete_after=10)
            logger.info('Syncing Commands')
            await bot.sync_commands()
        except:logger.error(traceback.format_exc())

@tasks.loop(seconds=5)
async def status_msg():
    """
    The `status_msg` function updates the performance information of a bot in a Discord channel and
    calculates the average load time.
    """
    settings = Settings()
    chan = bot.get_channel(settings.statuschannel_id) or await bot.fetch_channel(settings.statuschannel_id)
    del settings
    messages = await chan.history(limit=None).flatten()
    self_msgs = [message for message in messages if message.author == bot.user]
    if len(self_msgs) > 1:
        for message in self_msgs:
            await message.delete()
    self_msgs = [message for message in messages if message.author == bot.user]
    if len(self_msgs) == 1:
        msg = self_msgs[0]
    text = f'Bot was ready in: {load_time}s\nAvg. time until ready: {avg_load_time}s'
    embed=discord.Embed(colour=0x2ecc71)
    embed.add_field(name='Performance Information:', value=text)
    embed.set_footer(text=f'Uptime: {str(datetime.timedelta(seconds=int(time.perf_counter() - bot_starttime)))}')
    self_msgs = [message for message in messages if message.author == bot.user]
    if len(self_msgs) == 0:
        msg = await chan.send(embed=embed,view=MyView())
    try:
        await msg.edit(embed=embed,view=MyView())
    except:
        msg = await chan.send(embed=embed,view=MyView())

@tasks.loop(seconds=10)
async def version_control():
    """
    The function `version_control` checks the version of the current file and restarts the program if a
    new version is detected.
    """
    try:
        with open(Path(sys.path[0],os.path.basename(__file__)), 'r') as f:
            lines = f.readlines(1)
            file_version = lines[0].strip('#Version: \n')
        if file_version and current_version != file_version:
            os.system('cls') if sys.platform == 'win32' else os.system('clear')
            print(f'Updated {bot.user.name}:\nbefore: {current_version}\nafter: {file_version}\n')
            os.execv(sys.executable, ['python'] + sys.argv)
    except:logger.error(traceback.format_exc())

async def restart():
    """
    The function restarts the bot by changing its presence to "Restarting" and then executing the
    Python script again.
    """
    try:
        await bot.change_presence(activity=discord.Game('Restarting'), status=discord.Status.idle)
        os.execv(sys.executable, ['python'] + sys.argv)
    except:logger.error(traceback.format_exc())

@bot.slash_command(guild_ids=[1109530644578582590], guild_only=True)
@commands.is_owner()
async def set_status(ctx, status:discord.Option(str)):
    Settings().update_settings(setting='bot_status', value=status)
    await ctx.respond(f"The bot's status has been updated to: \'{status}\'", delete_after=15, ephemeral=True)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.custom,
            name="Custom Status",
            state=status,
        )
    )

@bot.slash_command(guild_ids=[1109530644578582590], guild_only=True)
@commands.is_owner()
async def show_log(ctx):
    log = discord.File(fp=Path(sys.path[0], 'bot.log'))
    await ctx.respond(file=log, ephemeral=True, delete_after=120)

@bot.slash_command(guild_ids=[1109530644578582590], guild_only=True)
@commands.is_owner()
async def clear_log(ctx):
    with open (Path(sys.path[0], 'bot.log'), 'r+') as f:
        f.seek(0)
        f.truncate(0)
    await ctx.respond('Cleared the Log', ephemeral=True, delete_after=10)

@bot.slash_command(guild_ids=[1109530644578582590], guild_only=True)
@commands.is_owner()
async def killbot(ctx):
    try:
        await ctx.defer()
        logger.info("Bot Closed")
        await bot.close()
        sys.exit(1)
    except:logger.error(traceback.format_exc())

@bot.event
async def on_connect():
    pass

@bot.event
#localization: MissingPermissions, NotOwner
async def on_command_error(ctx, error):
    """
    The function `on_command_error` handles different types of errors and sends appropriate responses
    based on the error type.
    """
    try:
        if isinstance(error, MissingPermissions):
            await ctx.respond('You do not have the necessary Permission(s).', ephemeral=True, delete_after=10)
        if isinstance(error, NotOwner):
            await ctx.respond('You do not have the necessary Permission(s).', ephemeral=True, delete_after=10)
    except:logger.error(traceback.format_exc())

@bot.event
async def on_ready():
    """
    The `on_ready` function is responsible for setting up the bot's initial state, as
    well as displaying the current version and setting a custom status.
    """
    try:
        set = Settings()
        global current_version
        with open(Path(sys.path[0],os.path.basename(__file__)), 'r') as f:
            l1 = f.readlines(1)
            current_version = l1[0].strip('#Version: \n')
        print(f'Version: {current_version}, Logged on as {bot.user}')
        logger.info(f'Version: {current_version}, Logged on as {bot.user}')  
        version_control.start()  
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.custom,
                name="Custom Status",
                state=set.bot_status,
            )
        )
        await bot_ready()
        status_msg.start()
    except:logger.error(traceback.format_exc())

async def bot_ready():
    global load_time, avg_load_time
    startup = StartupTimes(Path(sys.path[0], "bot.db"))
    bot_readytime = time.perf_counter()
    load_time = round(bot_readytime - bot_starttime, 2)
    load_times = startup.retrieve_startup_times()
    load_times.append(load_time)
    if len(load_times) > 20:
        while len(load_times) > 20:
            load_times.pop(0)
    startup.clear_startup_times()
    [startup.update_startup_times(lt) for lt in load_times]
    avg_load_time = round(sum(load_times)/len(load_times),2)
    
def run():
    """
    The function runs a bot by loading extensions and running it with the bot token.
    """
    try:
        with open(Path(sys.path[0], 'bot.log'), 'a', encoding='utf-8') as f:
            f.write(f"\n\n-----{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}-----\n")
        settings = Settings()
        for extension in bot_extensions: 
            try:    
                bot.load_extension(extension)
            except:logger.error(traceback.format_exc())
        bot.run(settings.bottoken)
    except:logger.error(traceback.format_exc())

global bot_starttime, bot_extensions
bot_starttime = time.perf_counter()
bot_extensions = ('cogs.generalutility', 'cogs.aboutme', 'cogs.setup')

#Declare all necessary Variables before this
run()