from discord.ext import commands
from discord import app_commands, Interaction
import discord
from hinoka import hinokaConfig
from higanhanaSdk.dc.embed import Embedx
from discord.utils import get
from discord.ui import View, Button

class Yahallo(View):
    """
   a view also asking if you want to apply for honkai or tof 
    """
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self._honkai_applied =False
        self._tof_applied = False

        
    @discord.ui.button(label="Apply Honkai Guild", style=discord.ButtonStyle.green)
    async def apply_honkai(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self._honkai_applied:
            self.stop()
            return
        
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=hinokaConfig.pending_impact_role))
        await interaction.response.send_message(f" {interaction.user.mention} Applied for Honkai guild")
        self._honkai_applied = True
    
    @discord.ui.button(label="Apply Tof Guild", style=discord.ButtonStyle.green)
    async def apply_tof(self,interaction: discord.Interaction, button: discord.ui.Button ):
        if self._tof_applied:
            self.stop()
            return
        
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=hinokaConfig.pending_tof_role))
        await interaction.response.send_message(f"{interaction.user.mention} Applied for Tof guild")
        self._tof_applied = True    
    
        
        
class cog_yahallo(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self._bot = bot
        self.yahallo_role = None
        self.clown_role = None
        self.chaotic_chat_channel = None
        self.induction_embed = Embedx.Success(
            "Welcome",
            """You have been inducted into the server.
            Check out <#943019261025189888> to pick your roles
            And <#1023072421001052190> for guides
            """
        )
        
        
    async def standard_guildeee_registry(self, ctx : Interaction):
        if self.chaotic_chat_channel is None:
            self.chaotic_chat_channel = self._bot.get_channel(hinokaConfig.chaotic_chat_channel)
        
        if not ctx.channel_id == 752408444165685298:
            return False
        
        if self.yahallo_role is None:
            self.yahallo_role = get(ctx.guild.roles, id=hinokaConfig.yahallo_role)
        
        if self.yahallo_role is None:
            raise Exception("yahallo role not found")
        
        if self.yahallo_role in ctx.user.roles:
            return False
        
        await ctx.user.add_roles(self.yahallo_role)

        await ctx.response.send_message(embed=self.induction_embed, view=Yahallo(timeout=20), ephemeral=True)

        return True
        
            
    @app_commands.command(name="yahallo", description="Inducts you into the server")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def yahallo(self, ctx : Interaction):
        await self.standard_guildeee_registry(ctx)
        await self.chaotic_chat_channel.send(f"a wild {ctx.user.mention} just appeared")
    
    @app_commands.command(name="yahello", description="Inducts you into the server")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def yahello(self, ctx : Interaction):
        results = await self.standard_guildeee_registry(ctx)
        
        if self.clown_role is None:
            self.clown_role = get(ctx.guild.roles, id=hinokaConfig.clown_card_holder)
            
        if results:
            await ctx.channel.send("You are a clown. Enjoy your clown card", ephemeral=True)
            await ctx.user.add_roles(self.clown_role)
        
        await self.chaotic_chat_channel.send(f"a wild {ctx.user.mention} clown just appeared")
            
        
async def setup(bot : commands.Bot):
    await bot.add_cog(cog_yahallo(bot))