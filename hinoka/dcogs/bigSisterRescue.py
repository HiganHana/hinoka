from time import sleep
import typing
from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta
from discordPyExt.components import EmbedX, CogX, Text, TextMappingTypes
from hinoka.cog.coop import PARTICIPANTS_OPTIONS
from hinoka.shared import config, storage
from hinoka.views.coop_banner import CoopBanner
from hinoka.embeds import placeholder
from hinoka.embeds.coop import *
from hinoka.cog.log import discord_api_log
from hinoka.cog.coop import *
from discord import app_commands

class cog_sisterRescue(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self._last_rescue_time = None
        self._check_for_big_sis_status.start()

    @tasks.loop(hours=3, reconnect=True)
    async def _check_for_big_sis_status(self):
        guild : discord.Guild = storage.get("GUILD")
        if guild is None:
            print("Guild not found")
            return
        
        big_sis_id = config.BIG_SIS_ID
        
        
        last_check_timestamp = config.get("LAST_RESCUE_CHECKED_TIMESTAMP")
        if last_check_timestamp is None:
            last_check_timestamp = datetime.utcnow().timestamp()
        else:
            last_check_timestamp = datetime.fromtimestamp(last_check_timestamp)    
        
        # if last check less than 3 hours ago, skip
        if datetime.utcnow() - last_check_timestamp < timedelta(hours=3):
            return await discord_api_log("Skipping rescue check, last check was less than 3 hours ago",
                last_check=Text(int(last_check_timestamp.timestamp()), TextMappingTypes.TIME),
                now=Text.Now()
            )
        
        # set LAST_RESCUE_CHECKED_TIMESTAMP
        config.noDupSet("LAST_RESCUE_CHECKED_TIMESTAMP", datetime.utcnow().timestamp())
        
        big_sis : discord.Member = guild.get_member(big_sis_id)
        
        # if big sis is online
        if big_sis.status == discord.Status.online:
            return await discord_api_log("Big sis is online", time=Text.Now())
            
        # if big sis is offline but last resuce time is less than 6 hours ago
        if self._last_rescue_time is not None and (datetime.utcnow() - self._last_rescue_time) < timedelta(hours=6):
            return await discord_api_log("Big sis is offline but last rescue time is less than 6 hours ago", time=Text.Now())
        
        # sister rescue
        await discord_api_log("Sister rescue time!", time=Text.Now())
        await self.sister_rescue()



    async def sister_rescue(self):
        sister_rescue_url = config.SISTER_RESCUE_URL
        token = config.SISTER_RESCUE_TOKEN
        import requests

        res = requests.post(sister_rescue_url, headers={"token" : token})
        await discord_api_log("Sister rescue request sent", time=Text.Now())    
    

    @app_commands.command(name="sisrescue", description="Hinoka rescuing big sis")
    @commands.has_any_role(*config.MOD_ROLES)
    @commands.cooldown(1, 60*60*24, commands.BucketType.user)
    async def sister_rescue(self, ctx: discord.Interaction):
        if self._check_for_big_sis_status.is_running():
            await ctx.response.send_message("already on the way for big sis", ephemeral=True)
            return
        
        self._check_for_big_sis_status.restart()
    
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_sisterRescue(bot))
