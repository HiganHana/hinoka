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
    @discord.ui.button(label="Apply Honkai Guild", style=discord.ButtonStyle.green)
    async def apply_honkai(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=hinokaConfig.pending_impact_role))
        await interaction.response.send_message("You have applied for the Honkai Guild", ephemeral=True)
        # disable
        button.disabled = True
        await interaction.message.edit(view=self)
        
    @discord.ui.button(label="Apply Tof Guild", style=discord.ButtonStyle.green)
    async def apply_tof(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=hinokaConfig.pending_tof_role))
        await interaction.response.send_message("You have applied for the Tof Guild", ephemeral=True)
        # disable
        button.disabled = True
        await interaction.message.edit(view=self)
            
    
        
class cog_yahallo(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self._bot = bot
        self.yahallo_role = None
        self.clown_role = None
        
        self.induction_embed = Embedx.Success(
            "Welcome",
            "You have been inducted into the server."
        )
        
        
    async def standard_guildeee_registry(self, ctx : Interaction):
        if self.yahallo_role is None:
            self.yahallo_role = get(ctx.guild.roles, id=hinokaConfig.yahallo_role)
        
        if self.yahallo_role is None:
            raise Exception("yahallo role not found")
        
        if self.yahallo_role in ctx.user.roles:
            return False
        
        await ctx.user.add_roles(self.yahallo_role)

        await ctx.response.send_message(embed=self.induction_embed, view=Yahallo(), ephemeral=True)

        return True
        
            
    @app_commands.command(name="yahallo")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def yahallo(self, ctx : Interaction):
        await self.standard_guildeee_registry(ctx)
    
    @app_commands.command(name="yahello")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def yahello(self, ctx : Interaction):
        results = await self.standard_guildeee_registry(ctx)
        
        if self.clown_role is None:
            self.clown_role = get(ctx.guild.roles, id=hinokaConfig.clown_card_holder)
            
        if results:
            await ctx.response.send_message("You are a clown. Enjoy your clown card", ephemeral=True)
            await ctx.user.add_roles(self.clown_role)
            
            
        
        
        