from discord.ui import View
import discord
from hinoka.cog.log import discord_api_log
from hinoka.embeds import you_already_has_this_role
from hinoka.embeds.coop import coop_banner_embedf, coop_thread_meta
from discordPyExt.components.text import Text
from hinoka.shared import config
from discordPyExt.components import Ctxl

class CoopBanner(View):
    def __init__(
        self, 
        *, 
        timeout = None,
    ):  
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="coop_banner_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        # get current thread id
        thread_id = interaction.message.channel.id
        
        # get role = COOP_{thread_id}
        role = discord.utils.get(interaction.guild.roles, name=f"COOP_{thread_id}")

        # check if user has role
        if role in interaction.user.roles:
            return await interaction.response.send_message(you_already_has_this_role.format(mention=interaction.user.mention), ephemeral=True)
        
        # add role to user
        await interaction.user.add_roles(role)
        
        # get embed
        embed = interaction.message.embeds[0]
        
        # embed keys
        embed_keys = coop_banner_embedf.extractKeys(embed)

        # get current participants
        current_participants = embed_keys.get("current_participants", "")
        
        current_count = embed_keys.get("current_count")

        reparsed = coop_banner_embedf.editEmbed(embed, 
            current_participants = f"{current_participants}\n{interaction.user.mention}\n",
            current_count = int(current_count) + 1,
        )

        # edit embed
        await interaction.message.edit(
            content=coop_thread_meta.format(
                current_count=int(current_count) + 1,
                max_participants=embed_keys.get("max_participants"),
                overflow=embed_keys.get("overflow"),
            ),
            embed=reparsed)
        
        await interaction.response.send_message(
            f"{interaction.user.mention} have joined the coop [{role.mention}]",
            allowed_mentions=discord.AllowedMentions(roles=True),
        )
    
    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, custom_id="coop_banner_leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        # get current thread id
        thread_id = interaction.message.channel.id
        
        # get embed
        embed = interaction.message.embeds[0]
        
        # get role = COOP_{thread_id}
        role = discord.utils.get(interaction.guild.roles, name=f"COOP_{thread_id}")

        # embed keys
        embed_keys = coop_banner_embedf.extractKeys(embed)

        # check if user is coordinator 
        coordinator_text = Text.fromRaw(embed_keys.get("coordinator"))
        
        coordinator_id = int(coordinator_text.text)
        if interaction.user.id == coordinator_id:
            return await interaction.response.send_message("You are the coordinator, you can't leave", ephemeral=True)

        # check if user has role
        if role not in interaction.user.roles:
            return await interaction.response.send_message(you_already_has_this_role.format(mention=interaction.user.mention), ephemeral=True)
        
        # remove role from user
        await interaction.user.remove_roles(role)
                
        # get current participants
        current_participants = embed_keys.get("current_participants", "")
        
        current_count = embed_keys.get("current_count")

        current_participants = current_participants.replace(f"{interaction.user.mention}", "")

        reparsed = coop_banner_embedf.editEmbed(embed, 
            current_participants = current_participants,
            current_count = int(current_count) - 1,
        )

        # edit embed
        await interaction.message.edit(
            content=coop_thread_meta.format(
                current_count=int(current_count) - 1,
                max_participants=embed_keys.get("max_participants"),
                overflow=embed_keys.get("overflow"),
            ),
            embed=reparsed
        )
        
        await interaction.response.send_message(f"You have left the coop {interaction.user.mention}", ephemeral=True)
        
    @discord.ui.button(label="Disband", style=discord.ButtonStyle.grey, custom_id="coop_banner_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # get current thread id
        thread_id = interaction.message.channel.id
        
        # get embed
        embed = interaction.message.embeds[0]
        
        # get role = COOP_{thread_id}
        role = discord.utils.get(interaction.guild.roles, name=f"COOP_{thread_id}")

        # embed keys
        embed_keys = coop_banner_embedf.extractKeys(embed)

        # check if user is coordinator 
        coordinator_text = Text.fromRaw(embed_keys.get("coordinator"))
        
        coordinator_id = int(coordinator_text.text)
        if not any((
            interaction.user.id == coordinator_id,
            Ctxl.has_any_role(interaction, config.MOD_ROLES),
            # admin 
            interaction.user.guild_permissions.administrator
        )):
            return await interaction.response.send_message("You are not the coordinator or you don't have permissions", ephemeral=True)

        # delete role
        await role.delete()

        # delete thread
        await interaction.channel.delete()

        # log
        await discord_api_log(f"{interaction.user} has disbanded the coop {role.id}")
        
    @discord.ui.button(label="🔃", style=discord.ButtonStyle.blurple, custom_id="coop_banner_fix")
    async def fix(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        check the current participants and refresh embed
        """
        
        # get current thread id
        thread_id = interaction.message.channel.id
        
        # get embed
        embed = interaction.message.embeds[0]
        
        # get role = COOP_{thread_id}
        role = discord.utils.get(interaction.guild.roles, name=f"COOP_{thread_id}")

        # embed keys
        embed_keys = coop_banner_embedf.extractKeys(embed)

        # check if user is coordinator 
        coordinator_text = Text.fromRaw(embed_keys.get("coordinator"))
        
        coordinator_id = int(coordinator_text.text)
        if not any((
            interaction.user.id == coordinator_id,
            Ctxl.has_any_role(interaction, config.MOD_ROLES),
            # admin 
            interaction.user.guild_permissions.administrator
        )):
            return await interaction.response.send_message("You are not the coordinator or you don't have permissions", ephemeral=True)

        # get current participants
        current_participants = embed_keys.get("current_participants", "")
        
        current_count = embed_keys.get("current_count")

        # get members with role
        members = role.members

        # get mentions
        mentions = [member.mention for member in members]

        # get mentions text
        mentions_text = "\n".join(mentions)

        # edit embed
        reparsed = coop_banner_embedf.editEmbed(embed, 
            current_participants = mentions_text,
            current_count = len(members)+1,
        )

        # edit embed
        await interaction.message.edit(
            content=coop_thread_meta.format(
                current_count=len(members)+1,
                max_participants=embed_keys.get("max_participants"),
                overflow=embed_keys.get("overflow"),
            ),
            embed=reparsed
        )
        
        await interaction.response.send_message(f"Fixed the coop {role.id}", ephemeral=True)