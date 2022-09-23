import asyncio
from datetime import datetime, timedelta
from time import sleep
import typing
from discord.ext import commands, tasks
from discord import app_commands, Interaction, ForumChannel, Thread
import discord
from hinoka import hinokaConfig
from higanhanaSdk.dc.embed import Embedx
from hinoka.cogs.coop import CoopEmbed, COOP_TYPE_LITERAL
import hinoka
import pytz

utc=pytz.UTC

class cog_coop(commands.GroupCog, group_name="coop", group_description="Coop commands"):
    def __init__(self, bot : commands.Bot):
        self._bot = bot
        self._coop_channel = None
        self._cached_threads = {}
        super().__init__()
        self.remove_expired_role_task.start()

    @tasks.loop(hours=24)
    async def remove_expired_role_task(self):
        """
        Check if there are new coop threads.
        """
        """
        Check if the coop channel is set and if it is, return it.
        """
        guild = await self._bot.fetch_guild(728455513532006491)
        guild : discord.Guild
        
        # get all roles prefixed with "COOP_"
        coop_roles = [role for role in guild.roles if role.name.startswith("COOP_")]
        utc_now =datetime.utcnow()
        for role in coop_roles:
            if role.created_at + timedelta(hours=48) < utc.localize(utc_now):
                await role.delete()
                print(f"Deleted role {role.name}")
        
        if self._coop_channel is None:
            self._coop_channel : ForumChannel = await self._bot.fetch_channel(hinokaConfig.COOP_FORUM)

    @app_commands.command(name="create", description="Create a coop post (use the other command to create tof stargate)")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def create(self, 
        ctx : Interaction,
        type : COOP_TYPE_LITERAL,
        name : str = "", 
        max_participants : int = None,
    ):  
        
        coop = CoopEmbed.create(
            name=name,
            type=type,
            author=ctx.user,
            max_participants=max_participants,
        )

        embed, title = await coop.to_embed(ctx)
        
        # apply role to user
        await ctx.user.add_roles(coop.role)
        
        # create thread post in forum channel
        thread, msg = await self._coop_channel.create_thread(
            name=title, 
            auto_archive_duration=1440, 
            reason=f"Coop created by {ctx.user} for {coop.type}", 
            embed=embed
        )
        
        await thread.add_user(ctx.user)
    
        #
        await ctx.response.send_message(
            embed=Embedx(
                title="Coop created",
                description=f"See your coop at {thread.mention}, role is {coop.role.mention}",
            )
        )
        
        self._cached_threads[thread.id] = coop
        
    @app_commands.command(name="join", description="Join a coop post (must use within the post)")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def join(self, ctx : Interaction):
        # get current thread
        thread : Thread = ctx.channel
        if not isinstance(thread, Thread):
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread."),
                ephemeral=True
            )
            
        # check if thread is in coop channel
        if thread.parent_id != hinokaConfig.COOP_FORUM:
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread."),
                ephemeral=True

            )
    
        # get coop embed (first message)
        msg : discord.Message = await thread.fetch_message(thread.id)
        embed : discord.Embed = msg.embeds[0]
        
        if thread.id not in self._cached_threads:
            coop = await CoopEmbed.create_from_embed(self._bot, ctx.guild,thread.name,embed)
        else:
            coop = self._cached_threads[thread.id]
        
        # if already has the role
        if coop.role in ctx.user.roles:
            return await ctx.response.send_message(
                embed=Embedx.Error("You are already in this coop."),
                ephemeral=True
            )
        
        # if coop is full
        if not (coop.current_participants < coop.max_participants):
            return await ctx.response.send_message(
                embed=Embedx.Error("This coop is full."),
                ephemeral=True
            )
    
        # add role to user
        await ctx.user.add_roles(coop.role)
        coop.current_participants += 1

        await ctx.response.send_message(
            embed=Embedx(
                title="You have joined the coop.",
            ), ephemeral=True
        )
        

        await thread.send(f"{ctx.user.mention} has joined the coop.")
        await thread.edit(name=coop.title)

        if thread.id not in self._cached_threads:
            self._cached_threads[thread.id] = coop
    
    @app_commands.command(name="leave", description="Leave a coop (must use within the post)")
    @commands.cooldown(1, 150, commands.BucketType.user)
    async def leave(self, ctx : Interaction):
        # get current thread
        thread : Thread = ctx.channel
        if not isinstance(thread, Thread):
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
            
        # check if thread is in coop channel
        if thread.parent_id != hinokaConfig.COOP_FORUM:
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
    
        # get coop embed (first message)
        msg : discord.Message = await thread.fetch_message(thread.id)
        embed : discord.Embed = msg.embeds[0]
        
        if thread.id not in self._cached_threads:
            coop = await CoopEmbed.create_from_embed(self._bot, ctx.guild,thread.name,embed)
        else:
            coop = self._cached_threads[thread.id]
        
        # if already
        if coop.role not in ctx.user.roles:
            return await ctx.response.send_message(
                embed=Embedx.Error("You are not in this coop.")
            )
        
        # remove role from user
        await ctx.user.remove_roles(coop.role)
        coop.current_participants -= 1

        await ctx.response.send_message(
            embed=Embedx(
                title=f"{ctx.user.mention} left the coop.",
            )
        )

        await thread.send(f"{ctx.user.mention} has left the coop.")
        await thread.edit(name=coop.title)

        if thread.id not in self._cached_threads:
            self._cached_threads[thread.id] = coop
        
    @app_commands.command(name="disband", description="Disband a coop (must use within the post)")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def disband(self, ctx : Interaction):
        # get current thread
        thread : Thread = ctx.channel
        if not isinstance(thread, Thread):
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
            
        # check if thread is in coop channel
        if thread.parent_id != hinokaConfig.COOP_FORUM:
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
    
        # get coop embed (first message)
        msg : discord.Message = await thread.fetch_message(thread.id)
        embed : discord.Embed = msg.embeds[0]
        
        if thread.id not in self._cached_threads:
            coop = await CoopEmbed.create_from_embed(self._bot, ctx.guild,thread.name,embed)
        else:
            coop = self._cached_threads[thread.id]
        
        # if not author
        if ctx.user != coop.author and not ctx.user.guild_permissions.administrator:
            return await ctx.response.send_message(
                embed=Embedx.Error("You are not the coordinator of this coop.")
            )
        
        # delete role
        await coop.role.delete()
        
        await ctx.response.send_message(
            embed=Embedx(
                title="Coop has been disbanded.",
            )
        )
        
        # delete thread
        await thread.delete()
        
        
        
        if thread.id in self._cached_threads:
            del self._cached_threads[thread.id]
    
    @app_commands.command(name="summon", description="Summon all participants (must use within the post)")
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def summon(self, ctx : Interaction):
        # get current thread
        thread : Thread = ctx.channel
        if not isinstance(thread, Thread):
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
            
        # check if thread is in coop channel
        if thread.parent_id != hinokaConfig.COOP_FORUM:
            return await ctx.response.send_message(
                embed=Embedx.Error("This command can only be used in a coop thread.")
            )
    
        # get coop embed (first message)
        msg : discord.Message = await thread.fetch_message(thread.id)
        embed : discord.Embed = msg.embeds[0]
        
        if thread.id not in self._cached_threads:
            coop = await CoopEmbed.create_from_embed(self._bot, ctx.guild,thread.name,embed)
        else:
            coop = self._cached_threads[thread.id]
        
        # if not author
        if ctx.user != coop.author:
            return await ctx.response.send_message(
                embed=Embedx.Error("You are not the coordinator of this coop.")
            )
        
        # get all members with coop role
        members = [m for m in ctx.guild.members if coop.role in m.roles]
        for member in members:
            sleep(0.5)
            await thread.send(f"summoning {member.mention}")

        await ctx.response.send_message("done", ephemeral=True)
    
    @app_commands.command(name="tof_stargate", description="Create a stargate tof coop")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def tof_stargate(self, 
        ctx : Interaction, 
        rarity : typing.Literal['⭐', '⭐⭐', '⭐⭐⭐'],
        type : typing.Literal["Booster Frame", "Nano Coating", "Nanofiber Frame", "Acidproof Glaze"],
        name : str = None,
    ):
        booster_frame_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/3/3d/Icon_Item_Booster_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160142"
        booster_frame_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/6/6e/Icon_Item_Booster_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160143"
        nano_coating_1 =  "https://static.wikia.nocookie.net/toweroffantasy/images/7/79/Icon_Item_Nano_Coating_I.png/revision/latest/scale-to-width-down/80?cb=20220819160147"
        nano_coating_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/c/cc/Icon_Item_Nano_Coating_II.png/revision/latest/scale-to-width-down/80?cb=20220819160149"
        nanofiber_1 ="https://static.wikia.nocookie.net/toweroffantasy/images/5/56/Icon_Item_Nanofiber_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160153"
        nanofiber_2 ="https://static.wikia.nocookie.net/toweroffantasy/images/8/8d/Icon_Item_Nanofiber_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160155"
        acidproof_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/b/b0/Icon_Item_Acidproof_Glaze_I.png/revision/latest/scale-to-width-down/80?cb=20220819160136"
        acidproof_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/8/83/Icon_Item_Acidproof_Glaze_II.png/revision/latest/scale-to-width-down/80?cb=20220819160138"

        if type == "Booster Frame" and rarity == "⭐":
            image = booster_frame_1
        elif type == "Booster Frame" and rarity[0:2] == "⭐⭐" :
            image = booster_frame_2
        elif type == "Nano Coating" and rarity == "⭐":
            image = nano_coating_1
        elif type == "Nano Coating" and rarity[0:2] == "⭐⭐":
            image = nano_coating_2
        elif type == "Nanofiber Frame" and rarity == "⭐":
            image = nanofiber_1
        elif type == "Nanofiber Frame" and rarity[0:2] == "⭐⭐":
            image = nanofiber_2
        elif type == "Acidproof Glaze" and rarity == "⭐":
            image = acidproof_1
        elif type == "Acidproof Glaze" and rarity[0:2] == "⭐⭐":
            image = acidproof_2
        
        if name is None:
            name = ""
            
        name = f"TOF-Gate {rarity}{name}"
        
        coop = CoopEmbed.create(
            name=name,
            type="TOF Stargate",
            author=ctx.user,
            max_participants=4,
        )

        embed, title = await coop.to_embed(ctx)
        embed.add_field(name="Stargate Type", value=f"{type}", inline=False)
        embed.set_thumbnail(url=image)
        
        # apply role to user
        await ctx.user.add_roles(coop.role)
        
        # create thread post in forum channel
        thread, msg = await self._coop_channel.create_thread(
            name=title, 
            auto_archive_duration=1440, 
            reason=f"Coop created by {ctx.user} for {coop.type}", 
            embed=embed,
        )
        thread : discord.Thread
        
        await thread.add_user(ctx.user)
    
        #
        await ctx.response.send_message(
            embed=Embedx(
                title="Coop created",
                description=f"See your coop at {thread.mention}, role is {coop.role.mention}",
            )
        )
        
        self._cached_threads[thread.id] = coop
    
    @app_commands.command(name="prune", description="delete all coop posts (not locked)")
    # admin
    @commands.has_permissions(administrator=True)
    async def prune(self, ctx : Interaction):
        # get all threads in channel
        self._coop_channel = await self._bot.fetch_channel(self._coop_channel.id)
        
        threads = self._coop_channel.threads
        for thread in threads:
            thread : discord.Thread
            if not thread.archived:
                continue
            if thread.locked:
                continue
            if thread.flags.pinned:
                continue
            
            await thread.delete()
            
        await ctx.response.send_message("done", ephemeral=True)
    
    
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_coop(bot))