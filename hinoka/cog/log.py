
from discord.ext import commands
from hinoka.shared import config, storage
import discord
from discordPyExt.components import EmbedFactory, Text

log_embed = EmbedFactory(
    title="Log",
    description="{timestamp}::{message}",
    color=0x00ff00,
)

async def discord_api_log(message : str, **kwargs):
    if storage.get("LOG_CHANNEL") is None:
        return
    
    channel : discord.TextChannel= storage["LOG_CHANNEL"]
    
    embed=log_embed.build(
        timestamp=Text.Now(), 
        message=message
    )
    
    for k, v in kwargs.items():
        embed.add_field(name=k, value=v)
    
    await channel.send(
        embed=embed
    )
        