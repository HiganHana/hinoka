from discord.ext import commands
from discord import app_commands, Interaction
import discord
from hinoka import hinokaConfig
from higanhanaSdk.dc.embed import Embedx

class cog_configer(commands.GroupCog, group_name="hinoka_config", group_description="Hinoka's configer"):
    def __init__(self, bot : commands.Bot):
        self._bot = bot
    
    @app_commands.command(name="set")
    @commands.has_guild_permissions(administrator=True)
    async def set(
        self, 
        ctx : Interaction,
        key : str, 
        value : str = None, 
        value_channel : discord.TextChannel = None, 
        value_role : discord.Role = None,
        value_user : discord.User = None
    ):
        if value is not None:
            hinokaConfig.setField(key, value)
        elif value_channel is not None:
            hinokaConfig.setField(key, [value_channel.id, "CHANNEL"])
            await ctx.response.send_message(embed=Embedx.Success(f"Set {key} to {value_channel.mention}"))
        elif value_role is not None:
            hinokaConfig.setField(key, [value_role.id, "ROLE"])
            await ctx.response.send_message(
                embed=Embedx.Success(f"Set {key} to {value_role.mention}"),  
                allowed_mentions=discord.AllowedMentions(roles=False)
            )
        elif value_user is not None:
            hinokaConfig.setField(key, [value_user.id, "USER"])
            await ctx.response.send_message(
                embed=Embedx.Success(f"Set {key} to {value_user.mention}"),  
                allowed_mentions=discord.AllowedMentions(users=False)
            )
        else:
            await ctx.response.send_message(
                embed=Embedx.Warning("Please provide a valid value")
            )
            
    @app_commands.command(name="get")
    @commands.has_guild_permissions(administrator=True)
    async def get(self, ctx : Interaction, key : str):
        property = None
        value = hinokaConfig.getField(key)
        if isinstance(value, list) and isinstance(value[0], int):
            if value[1] == "CHANNEL":
                value = await self._bot.fetch_channel(value[0])
                property = "CHANNEL"
            elif value[1] == "ROLE":
                value = ctx.guild.get_role(value[0])
                property = "ROLE"
            elif value[1] == "USER":
                value = await self._bot.fetch_user(value[0])
                property = "USER"
        
        if value is None:
            await ctx.response.send_message(
                embed=Embedx.Warning(f"No value found for {key}")
            )
        else:
            embed = Embedx.Success(title="Config Value: " + key)
            if property is None:
                embed.add_field(name="value", value=value)
            else:
                embed.add_field(name="value", value=f"{value}")
                embed.add_field(name=f"value (parsed to {property})", value=f"{value.mention}", inline=False)
            await ctx.response.send_message(
                embed= embed,
                allowed_mentions=discord.AllowedMentions(users=False, roles=False)
            )
    
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_configer(bot))