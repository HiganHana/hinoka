import logging, sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
from discordPyExt.setup import DcDeployer
from discordPyExt.components import BotX
from discordPyExt.setup.ext import DeployFlask
import discord
from hinoka.shared import config, storage
from hinoka.views.coop_banner import CoopBanner
import typing

from hinoka.cog.log import discord_api_log


class CustomBotX(BotX):
    def __init__(self, command_prefix="!", intents = None) -> None:
        super().__init__(command_prefix, intents)

    async def setup_hook(self) -> None:
        await super().setup_hook()
        self.add_view(CoopBanner())
        
    async def on_ready(self):
        await super().on_ready()
        storage.LOG_CHANNEL = self.get_channel(config.LOG_CHANNEL)
        
        if storage.get("COOP_CHANNEL") is None:
            storage.COOP_CHANNEL = await self.fetch_channel(config.COOP_CHANNEL)
            await discord_api_log("Coop Channel inited")

    
deployer = DcDeployer(
    extensions=[],
    path='hinoka',
    storage=storage,
    config=config,
    DISCORD_BOT_INTENTS= discord.Intents.default(),
    DISCORD_OBJ = CustomBotX
)

if __name__ == '__main__':
    deployer.run()