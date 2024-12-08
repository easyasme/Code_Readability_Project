import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import logging
import asyncio
import os
import traceback
from minecraftTellrawGenerator import MinecraftTellRawGenerator as tellraw

import config

LOG = logging.getLogger("BACKUP")

async def run_command_subprocess(command: str, timeout: int = 900):
    """
    Run a command in a subprocess.
    """
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise
    return stdout.decode(), stderr.decode(), proc.returncode


class BackupsCog(commands.Cog):
    """
    This cog controls server backups and restores.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_backup.start()
        self.backed_up_offline = False

    async def backup_server(self, backup_type: str):
        """
        Backup the server.
        """
        LOG.info("Backing up server.")

        file_name = "backup-{type}-{date}-{time}.zip".format(
            type=backup_type,
            date=datetime.datetime.now().strftime('%Y-%m-%d'),
            time=datetime.datetime.now().strftime('%H-%M-%S')
        )

        file_name = os.path.join(config.backups["backup_location"], file_name)

        command = f"zip -r {file_name} {config.backups['world_location']}"

        LOG.info(f"Command: {command}")

        stdout, stderr, returncode = await run_command_subprocess(command)

        if returncode != 0:
            LOG.warn(f"Failed to backup server: {stderr}")

            LOG.warn(f"Removing partial backup: {file_name}")
            # We should be careful that we're not wildly deleting things here.
            os.remove(file_name)
        else:
            LOG.info("Server backup complete.")

        return returncode, stderr

    
    # Back up the server. Returns true on success, false any time else.
    async def backup_wrapper(self, backup_type: str) -> bool:
        # Step 1: Backup the server.
        try:
            backup_name = "Manual"
            if backup_type == "hourly":
                backup_name = "Hourly"
            else:
                backup_name = "Automatic"


            # Notify players on the server a backup is occurring.
            try:
                await self.bot.send_server_command("tellraw @a " + tellraw.multiple_tellraw(
                    tellraw(text="["),
                    tellraw(text="Server",color="red"),
                    tellraw(text="] "),
                    tellraw(text=f"{backup_name} server backup starting, the game may lag for a bit!",color="yellow")
                ))
                self.backed_up_offline = False
            except:
                # If we can't send the message, the server is offline.
                if self.backed_up_offline and backup_type != "manual":
                    LOG.warn("Server is offline, skipping automatic backup.")
                    return False
                self.backed_up_offline = True
            
            # Force the server to save the world.
            try:
                await self.bot.send_server_command("save-all")
                
                # Wait for the save to complete.
                await asyncio.sleep(5)
            
                await self.bot.send_server_command("save-off")
            except:
                # It is fine if the server is offline, but we should log it.
                LOG.warn("Server must be offline, save-all/save-off failed.")


            returncode, stderr = await self.backup_server(backup_type)

            # Turn the server save back on.
            try:
                await self.bot.send_server_command("save-on")
            except Exception as e:
                # It should *mostly* be fine if the server is offline, but we
                # will log this just in case there is some other actual error.
                LOG.warn(f"Failed to turn server save back on: {e}")
                if not self.bot.block_chat:
                    LOG.error("Server chat is not blocked, but failed to send save-on command.")

            if returncode != 0:
                LOG.error(f"Failed to backup server (code {returncode}): {stderr}")
                await self.bot.notification_channel.send(
                    embed=discord.Embed(
                        color=0xff0000,
                        description=f":x: **Failed to backup server ({backup_type}, code {returncode}): {stderr}**"
                    )
                )

                # Notify players on the server the backup failed.
                await self.bot.send_server_command("tellraw @a " + tellraw.multiple_tellraw(
                    tellraw(text="["),
                    tellraw(text="Server",color="red"),
                    tellraw(text="] "),
                    tellraw(text="Server backup failed!",color="red")
                ))
                return False
            else:
                # Notify players on the server the backup is complete.
                await self.bot.send_server_command("tellraw @a " + tellraw.multiple_tellraw(
                    tellraw(text="["),
                    tellraw(text="Server",color="green"),
                    tellraw(text="] "),
                    tellraw(text="Server backup complete!",color="yellow")
                ))
                return True
        except Exception as e:
            LOG.error(f"Failed to backup server, threw exception: {type(e).__name__}, args: {e.args}, str: {e}")
            try:
                self.bot.notifications
                await self.bot.notification_channel.send(
                    embed=discord.Embed(
                        color=0xff0000,
                        description=f":x: **Failed to backup server ({backup_type}, exception): {e}**"
                    )
                )
            except:
                None

            try:
                # Notify players on the server the backup failed.
                await self.bot.send_server_command("tellraw @a " + tellraw.multiple_tellraw(
                    tellraw(text="["),
                    tellraw(text="Server",color="red"),
                    tellraw(text="] "),
                    tellraw(text="Server backup failed!",color="red")
                ))
            except:
                None

            return False

        return False # This should never be reached, but return false just in case cosmic rays hit the server or something.

    def get_backups(self):
        # 1.a) Get a list of all backups.
        backups = []
        for file in os.listdir(config.backups["backup_location"]):
            if file.endswith(".zip"):
                backups.append(file)
                LOG.debug("Found file: " + file)
        
        # 1.b) Sort the backups by:
        #     - Hourly backups, newest first.
        #     - Daily backups, newest first.
        #     - Weekly backups, newest first.
        hourly = []
        daily = []
        weekly = []
        others = []

        for backup in backups:
            if "hourly" in backup:
                hourly.append(backup)
            elif "daily" in backup:
                daily.append(backup)
            elif "weekly" in backup:
                weekly.append(backup)
            else:
                others.append(backup)
        
        hourly.sort(reverse=True)
        daily.sort(reverse=True)
        weekly.sort(reverse=True)

        return hourly, daily, weekly, others

    async def cleanup_backups(self):
        """
        Clean up the backup directory, keeping only the specified number of hourly, daily, and weekly backups.
        """

        LOG.info("Cleaning up backup directory.")
        
        # 1.a) Get the backups
        hourly, daily, weekly, others = self.get_backups()

        LOG.info(f"Found {len(hourly)} hourly backups, {len(daily)} daily backups, and {len(weekly)} weekly backups.")
        if len(others) > 0:
            LOG.warn(f"Found {len(others)} other files in the backups folder.")

        # 2) Remove any backups that exceed the maximum number of backups.
        #     - Hourly backups, keep the newest x backups.
        #     - Daily backups, keep the newest x backups.
        #     - Weekly backups, keep the newest x backups.

        # 2.a) Remove hourly backups. If the newest daily backup is older than 
        # 24 hours, convert the hourly backup to a daily backup instead of 
        # deleting it.
        while len(hourly) > config.backups["hourly_backup_count"]:
            oldest_hourly = hourly.pop()
            LOG.info(f"Removing hourly backup: {oldest_hourly}")
            # backup-weekly-%Y-%m-%d-%H-%M-%S.zip
            if len(daily) == 0 or datetime.datetime.now() - datetime.datetime.strptime(daily[0], 'backup-daily-%Y-%m-%d-%H-%M-%S.zip') > datetime.timedelta(days=1):
                LOG.info("Actually converting to daily backup.")
                # Rename the hourly backup to a daily backup.
                os.rename(os.path.join(config.backups["backup_location"], oldest_hourly), os.path.join(config.backups["backup_location"], oldest_hourly.replace("hourly", "daily")))

                # Add the new daily backup to the list of daily backups. Since
                # it should now be the newest, we can just insert it at the
                # beginning of the list.
                daily.insert(0, oldest_hourly.replace("hourly", "daily"))
            else:
                LOG.debug(f"Remove: {os.path.join(config.backups['backup_location'], oldest_hourly)}")
                # Delete the hourly backup.
                os.remove(os.path.join(config.backups["backup_location"], oldest_hourly))
        
        # 2.b) Remove daily backups. If the newest weekly backup is older than
        # 7 days, convert the daily backup to a weekly backup instead of
        # deleting it.
        while len(daily) > config.backups["daily_backup_count"]:
            oldest_daily = daily.pop()
            LOG.info(f"Removing daily backup: {oldest_daily}")
            if len(weekly) == 0 or datetime.datetime.now() - datetime.datetime.strptime(weekly[0], 'backup-weekly-%Y-%m-%d-%H-%M-%S.zip') > datetime.timedelta(days=7):
                LOG.info("Actually converting to weekly backup.")
                # Rename the daily backup to a weekly backup.
                os.rename(os.path.join(config.backups["backup_location"], oldest_daily), os.path.join(config.backups["backup_location"], oldest_daily.replace("daily", "weekly")))

                # Add the new weekly backup to the list of weekly backups. Since
                # it should now be the newest, we can just insert it at the
                # beginning of the list.
                weekly.insert(0, oldest_daily.replace("daily", "weekly"))
            else:
                LOG.debug(f"Remove: {os.path.join(config.backups['backup_location'], oldest_daily)}")
                # Delete the daily backup.
                os.remove(os.path.join(config.backups["backup_location"], oldest_daily))

        # 2.c) Remove weekly backups.
        while len(weekly) > config.backups["weekly_backup_count"]:
            oldest_weekly = weekly.pop()
            LOG.info(f"Removing weekly backup: {oldest_weekly}")
            LOG.debug(f"Remove: {os.path.join(config.backups['backup_location'], oldest_weekly)}")
            os.remove(os.path.join(config.backups["backup_location"], oldest_weekly))
        
    
    async def digest_backups(self):
        """
        Digest the backups and send a message to the notification channel.
        """
        hourly, daily, weekly, others = self.get_backups()

        # 3) Send a message to the notification channel with the status of the
        # backups.
        try:
            hourly, daily, weekly, others = self.get_backups()

            embed = discord.Embed(
                title="Backup Digest",
                color=0x00ff00,
                description="An hourly backup just completed, here is the status of the backups. All lists are displayed newest to oldest."
            )

            if len(hourly) > 0:
                embed.add_field(name="Hourly", value="```\n" + "\n".join(hourly) + "\n```", inline=False)
            if len(daily) > 0:
                embed.add_field(name="Daily", value="```\n" + "\n".join(daily) + "\n```", inline=False)
            if len(weekly) > 0:
                embed.add_field(name="Weekly", value="```\n" + "\n".join(weekly) + "\n```", inline=False)
            if len(others) > 0:
                embed.add_field(name="Other", value="```\n" + "\n".join(others) + "\n```", inline=False)

            await self.bot.notification_channel.send(
                embed=embed
            )
        except:
            LOG.error(f"Failed to send backup digest to notification channel: {traceback.format_exc()}")
    
    async def _auto_backup(self):
        LOG.info("Starting automatic backup...")
        if (await self.backup_wrapper("hourly")):
            await self.cleanup_backups()
            await self.digest_backups()
        else:
            await self.bot.notification_channel.send(":x: **Failed to backup server (automatic, hourly)**")

    # @app_commands.checks.cooldown(1, 180.0)

    @app_commands.command(name="backup-now", description="Backup the minecraft server right now.")
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_now(self, interaction: discord.Interaction, fake_hourly: bool=False) -> None:
        """
        Backup the minecraft server right now.
        """
        await interaction.response.defer(thinking=True)

        if fake_hourly:
            await self._auto_backup()
            await interaction.followup.send("Fake hourly backup complete.")
            return
        
        try:
            LOG.info("Manual backup starting...")
            ok = await self.backup_wrapper("manual")

            if ok:
                await interaction.followup.send("Server backup complete.")
            else:
                await interaction.followup.send(f"Failed to backup server, check logs for details.")
        except Exception as e:
            await interaction.followup.send("Failed to backup server: " + str(e))

            # Log stacktrace to console
            LOG.error(traceback.format_exc())

    @app_commands.command(name="restore", description="Restore a backup by its name.")
    @app_commands.describe(
        name="The name of the backup to restore."
    )
    @app_commands.checks.cooldown(1, 180.0)
    @app_commands.checks.has_permissions(administrator=True)
    async def restore(self, interaction: discord.Interaction, name: str) -> None:
        """
        Restore a backup.
        """
        await interaction.response.send_message("This command is not yet implemented.", ephemeral=True)
        # await interaction.response.defer(thinking=True)
    

    @app_commands.command(name="list-backups", description="List all backups.")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_backups(self, interaction: discord.Interaction) -> None:
        """
        List all backups.
        """
        await interaction.response.defer(thinking=True)

        try:
            hourly, daily, weekly, others = self.get_backups()

            embed = discord.Embed(
                title="Backups",
                color=0x00ff00,
                description="All lists are displayed newest to oldest."
            )

            def shorten_string(string: str, length: int = 1000) -> str:
                if len(string) > length:
                    return string[:length] + "..."
                return string

            if len(hourly) > 0:
                embed.add_field(name="Hourly", value="```\n" + shorten_string("\n".join(hourly)) + "\n```", inline=False)
            if len(daily) > 0:
                embed.add_field(name="Daily", value="```\n" + shorten_string("\n".join(daily)) + "\n```", inline=False)
            if len(weekly) > 0:
                embed.add_field(name="Weekly", value="```\n" + shorten_string("\n".join(weekly)) + "\n```", inline=False)
            if len(others) > 0:
                embed.add_field(name="Other", value="```\n" + shorten_string("\n".join(others)) + "\n```", inline=False)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed to get the list of backups: {e}")
    
    
    async def on_error(self, event, *args, **kwargs):
        LOG.error(f"Error in event {event}: {args} {kwargs}")


    @app_commands.command(name="stop-backups", description="Stop automatic backups.")
    @app_commands.checks.cooldown(1, 180.0)
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_backups(self, interaction: discord.Interaction) -> None:
        """
        Stop automatic backups.
        """
        if not self.auto_backup.is_running():
            await interaction.response.send_message("Automatic backups are not running.", ephemeral=True)
            return
        self.auto_backup.stop()
        await interaction.response.send_message("Automatic backups stopped.", ephemeral=True)


    @app_commands.command(name="start-backups", description="Start automatic backups.")
    @app_commands.checks.cooldown(1, 180.0)
    @app_commands.checks.has_permissions(administrator=True)
    async def start_backups(self, interaction: discord.Interaction) -> None:
        """
        Start automatic backups.
        """
        if self.auto_backup.is_running():
            await interaction.response.send_message("Automatic backups are already running.", ephemeral=True)
            return
        self.auto_backup.start()
        await interaction.response.send_message("Automatic backups started.", ephemeral=True)
    
    @app_commands.command(name="cleanup-backups", description="Clean up the backup directory. This is mostly for debugging purposes.")
    @app_commands.checks.has_permissions(administrator=True)
    async def cleanup_backups_command(self, interaction: discord.Interaction, wipe_others: bool=False) -> None:
        """
        Clean up the backup directory.
        """
        await interaction.response.defer(thinking=True)
        await self.cleanup_backups()
        await interaction.followup.send("Backup directory cleaned up.")

    @tasks.loop(hours=1)
    async def auto_backup(self):
        """
        Automatically backup the server.
        """
        await self._auto_backup()
        

    @commands.Cog.listener()
    async def on_ready(self):
        None

    async def cog_load(self):
        LOG.info("Backups cog is loading.")
        

    async def cog_unload(self):
        LOG.warn("Backups cog unloaded!")
        if self.auto_backup.is_running():
            self.auto_backup.stop()
        try:
            await self.bot.notification_channel.send(":warning: Backups cog unloaded.")
        except Exception as e:
            LOG.error(f"Failed to send cog unload notification: {e}")


async def setup(bot):
    await bot.add_cog(BackupsCog(bot))
