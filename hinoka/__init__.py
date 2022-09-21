
from hinoka.logger import logger

from higanhanaSdk.utils.config import Config as _config_
import hinoka.config as _config

hinokaConfig = _config_(_config)

import discord as _discord
from discord.ext import commands as _commands
from higanhanaSdk.dc.bot import load_extensions as _load_extensions

class hinokaBrain(_commands.Bot):
    async def on_ready(self):
        logger.info("Logged in as {0.user}".format(self))
            
    async def setup_hook(self) -> None:
        await _load_extensions(self, "hinoka/dcogs",config=hinokaConfig, logger=logger)
        await self.tree.sync()

    @classmethod
    def create(cls):
        intents = _discord.Intents.default()
        intents.members = True
        intents.message_content = True
        client = cls(command_prefix="!",intents=intents)
        
        return client
