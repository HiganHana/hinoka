from time import sleep
import typing
from discord.ext import commands, tasks
from discord import Message, app_commands, Interaction, ForumChannel, Thread
import discord
from discordPyExt.components import EmbedX, GroupCogX
from hinoka.cog.coop import PARTICIPANTS_OPTIONS
from hinoka.shared import config, storage
from hinoka.views.coop_banner import CoopBanner
from hinoka.embeds import placeholder
from hinoka.embeds.coop import *
from hinoka.cog.log import discord_api_log
from hinoka.cog.coop import *

class cog_coop(GroupCogX, group_name="coop", group_description="Hinoka's coop cog"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.coop_mapping_cache : typing.Dict = {}
        #
        super().__init__()

    async def _create_coop(
        self,
        ctx: Interaction,
        name : str,
        max_participants : PARTICIPANTS_OPTIONS = "No Limit",
        notes : str = None,
        allow_overflow : bool = False,
        embed_factory : EmbedFactory = coop_banner_embedf
    ):
        coop_channel : discord.ForumChannel = storage.COOP_CHANNEL

        if notes is None:
            notes = "N/A"
        
        # create thread
        threadwithMessage= await coop_channel.create_thread(
            name=f"{name}",
            embed=placeholder
        )
        
        thread  : Thread  = threadwithMessage.thread
        message : Message = threadwithMessage.message
        
        # create role
        role : discord.Role = await coop_channel.guild.create_role(
            name=f"COOP_{thread.id}",
            mentionable=True,
        )
        
        # add author to role
        await ctx.user.add_roles(role)
        
        # create banner
        banner = CoopBanner(timeout=None)
        
        # edit
        overflow= "⭐" if allow_overflow else "⚫"
        current_count = 1
        
        new_embed = embed_factory.build(
            current_count = current_count,
            max_participants = max_participants,
            current_participants = f"",
            coordinator=f"{ctx.user.mention}",
            overflow= overflow,
            role=role.mention,
            name=name,
            notes=notes
        )
        
        # add person to thread
        await thread.add_user(ctx.user)
        
        await message.edit(
            content=coop_thread_meta.format(
                current_count=current_count,
                max_participants=max_participants,
                overflow=overflow,
            ),
            embed=new_embed,
            view=banner,
        )
        
        # notify in channel
        await ctx.response.send_message(
            f"{ctx.user.mention} has created a new coop {thread.mention}",
        )

    @app_commands.command(name="create_new")
    @app_commands.describe(
        name= "Name of the coop",
        max_participants= "Maximum number of participants, default to no limit",
    )
    async def create_new(
        self, 
        ctx : Interaction, 
        name : str,
        max_participants : PARTICIPANTS_OPTIONS = "No Limit",
        notes : str = None,
        allow_overflow : bool = False,
    ):
        await self._create_coop(
            ctx,
            f"[COOP] {name}",
            max_participants,
            notes,
            allow_overflow,
        )
        

    
    @app_commands.command(name="create_preset")
    async def create_tof_preset(
        self,
        ctx : Interaction,
        preset : COOP_PRESETS,
        name : str = None,
        max_participants : PARTICIPANTS_OPTIONS = None,
        notes : str = None,
        allow_overflow : bool = False,
    ):
        if name is None:
            name = COOP_PRESETS_META[preset]["name"]
        else:
            name = f"[{COOP_PRESETS_META[preset]['name']}] {name}"
        
        await self._create_coop(
            ctx,
            name,
            max_participants = max_participants or COOP_PRESETS_META[preset]["max_participants"],
            notes = notes,
            allow_overflow = allow_overflow
        )
    
    @app_commands.command(name="create_tof_gate")
    async def create_tof_gate(
        self,
        ctx : Interaction,
        material : MATERIAL_TYPES,
        star : typing.Literal["⭐", "⭐⭐", "⭐⭐⭐"],
        name : str = None,
        notes : str = None,
    ):
        """
        Args:
            material (str): 'Booster Frame', 'Nano Coating', 'Nanofiber Frame', 'Acidproof Glaze'
            star (str): '⭐', '⭐⭐', '⭐⭐⭐'

        """
        await discord_api_log(f"{ctx.user} created a tof coop", 
            material=material,
            star=star, 
        )
        
        if material == "Booster Frame" and star != "⭐":
            factory = booster_frame_embedf2
        elif material == "Nano Coating" and star != "⭐":
            factory = nano_coating_embedf2
        elif material == "Nanofiber Frame" and star != "⭐":
            factory = nanofiber_embedf2
        elif material == "Acidproof Glaze" and star != "⭐":
            factory = acidproof_embedf2
        elif material == "Booster Frame" and star == "⭐":
            factory = booster_frame_embedf1
        elif material == "Nano Coating" and star == "⭐":
            factory = nano_coating_embedf1
        elif material == "Nanofiber Frame" and star == "⭐":
            factory = nanofiber_embedf1
        elif material == "Acidproof Glaze" and star == "⭐":
            factory = acidproof_embedf1
        else:
            raise ValueError("Invalid material or star")
        
        if notes is None:
            notes = ""
        
        if name is not None:
            notes = f"[{name}]{notes}"
        
        await self._create_coop(
            ctx=ctx,
            name=f"[TOF Gate] {material} {star}",
            max_participants=4,
            notes=notes,
            allow_overflow=False,
            embed_factory=factory
        )
        
        

    @app_commands.command(name="purge")
    @commands.has_any_role(*config.MOD_ROLES)
    async def purge_coop(
        self,
        ctx : Interaction,
    ):
        # get all guild roles starting with COOP_
        roles = {int(role.name.split("_")[1]): role for role in ctx.guild.roles if role.name.startswith("COOP_")}
                 
        # get all threads in coop channel
        coop_channel : ForumChannel = storage.COOP_CHANNEL
        threads : typing.Iterable[Thread] = coop_channel.threads
        threads : typing.Dict[int, Thread] = {thread.id: thread for thread in threads}
        
        await ctx.response.defer()
        
        # check if thread archived
        for id, role in roles.items():
        
            # check if thread is active
            if id in threads and not threads[id].archived:
                continue
        
            await role.delete()
            await discord_api_log(f"{ctx.user} purged {role.name}")
            # delete the thread
            await threads[id].delete()
    
        await ctx.channel.send("COOP Purge complete")
    
    
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_coop(bot))
