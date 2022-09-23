import asyncio
from pydoc import describe
from time import sleep
import typing
from discord.ext import commands, tasks
from discord import app_commands, Interaction, ForumChannel, Thread
import discord
from hinoka import hinokaConfig
from higanhanaSdk.dc.embed import Embedx
from hinoka.cogs.coop import CoopEmbed, COOP_TYPE_LITERAL
import hinoka


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
        
        if self._coop_channel is None:
            self._coop_channel : ForumChannel = await self._bot.fetch_channel(hinokaConfig.COOP_FORUM)
            
        # loop threads
        for thread in self._coop_channel.threads:
            
            if thread.archived and thread.id in self._cached_threads:
                self._cached_threads.pop(thread.id)
            
            if thread.archived:
                continue
            
            if thread.id in self._cached_threads:
                continue
            
            # get coop embed (first message)
            msg : discord.Message = await thread.fetch_message(thread.id)
            embed : discord.Embed = msg.embeds[0]
            self._cached_threads[thread.id] = await CoopEmbed.create_from_embed(self._bot, guild,thread.name,embed)
        
        coop_roles = [role for role in guild.roles if role.name.startswith("COOP")]
        
        all_recorded_coop_roles = [t.role for t in self._cached_threads.values() if t.role is not None]
            
        # get all coop roles not in all_recorded_coop_roles
        expired_roles = [role for role in coop_roles if role not in all_recorded_coop_roles]
        
        # remove expired roles
        for role in expired_roles:
            await role.delete()
    

    @app_commands.command(name="create")
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
        
    @app_commands.command(name="join")
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
    
    @app_commands.command(name="leave")
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
        
    @app_commands.command(name="disband")
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
        if ctx.user != coop.author:
            return await ctx.response.send_message(
                embed=Embedx.Error("You are not the coordinator of this coop.")
            )
        
        # delete role
        await coop.role.delete()
        
        # delete thread
        await thread.delete()
        
        await ctx.response.send_message(
            embed=Embedx(
                title="Coop has been disbanded.",
            )
        )
        
        if thread.id in self._cached_threads:
            del self._cached_threads[thread.id]
    
    @app_commands.command(name="summon")
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
        
    
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_coop(bot))