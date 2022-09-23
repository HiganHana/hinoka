from datetime import datetime, timedelta
from functools import cached_property
import typing
from uuid import uuid4
import discord
from pydantic import BaseModel, Field
from higanhanaSdk.dc.embed import Embedx
from discord.ext import commands

COOP_TYPE_LITERAL = typing.Literal[
    "Honkai lv1-80 raid",
    "Honkai lv81+ raid",
    "TOF Raid",
    "TOF Party",
    "TOF Stargate",
    "Party Game",
    "Other"
]

class CoopEmbed(BaseModel):
    name : str
    author : typing.Union[discord.User, discord.Member]
    expire_in : int
    role : discord.Role = None
    type : COOP_TYPE_LITERAL
    max_participants : int = None
    current_participants : int = 1
    created_at : datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data) -> None:
        super().__init__(**data)
        type_ = data.get("type")
        if self.max_participants is None:
            self.max_participants = -1
        if (type_ == "Honkai lv1-80 raid" or type_ == "Honkai lv81+ raid") and not 1<=self.max_participants<=3:
            self.max_participants = 3
        elif type_ == "TOF Raid" and not 1<=self.max_participants<=8:
            self.max_participants = 8
        elif (type_ == "TOF Party" or type_ == "TOF Stargate") and not 1<=self.max_participants<=4:
            self.max_participants = 4

        if self.name is None or self.name == "":
            self.name = type_
        
        object.__setattr__(self, "expire_time", self.created_at + timedelta(seconds=self.expire_in))
    
    @property
    def gotta_add_waitlist(self):
        return self.current_participants >= self.max_participants
    
    async def add_participant(self, ctx : discord.Interaction, user : typing.Union[discord.User, discord.Member]):
        if self.role is None:
            
            timestamp = int(self.expire_time.timestamp())
            
            role_name = "COOP_" + timestamp
            new_role = await ctx.guild.create_role(
                name=role_name, 
                colour = discord.Colour.red(), 
                mentionable=True,
            )
            # put to bottom
            self.role = new_role
        

        await user.add_roles(self.role)
        
    
    async def to_embed(self, ctx : discord.Interaction):
        """
        Convert this CoopEmbed to a discord.Embed
        """

        embed = Embedx.Success(f"Coop Banner")
            
        await self.add_participant(ctx, ctx.user)    
        
        embed.add_field(name="Role", value=self.role.mention)
        #
        embed.add_field(name="Coordinator", value=self.author.mention)
        embed.add_field(name="Type", value=self.type)
        
        if self.max_participants:
            embed.add_field(name="Max Participants", value=self.max_participants)
            
        return embed, self.title
    
    @property
    def title(self):
        return f"{self.name} ({self.current_participants} out of {self.max_participants})"
    
    @classmethod
    def create(
        cls,
        name : str,
        author : discord.User,
        type : COOP_TYPE_LITERAL,
        max_participants : int = None,
        expire_in : int = 60*24
    ):
        return cls(
            name=name,
            author=author,
            type=type,
            max_participants=max_participants,
            expire_in=expire_in
        )
    
    @classmethod
    async def create_from_embed(cls,bot: commands.Bot, guild : discord.Guild, title: str, embed : discord.Embed):
        """
        Create a CoopEmbed from a discord.Embed
        """
        name = title
        name, participants_bit = name.split(" (")
        name = name.strip()
        participants_bit = participants_bit.strip(")")
    
        current_participants, max_participants = participants_bit.split("out of")
        current_participants = int(current_participants)
        max_participants = int(max_participants)
        
        author = embed.fields[1].value
        author = author.strip("<@!>")
        author = int(author)
        author = await bot.fetch_user(author)
        
        role = embed.fields[0].value
        role = role.strip("<@&>")
        role = int(role)
        role = guild.get_role(role)
        
        type_ = embed.fields[2].value
            
        return cls(
            name=name,
            author=author,
            role=role,
            type=type_,
            max_participants=max_participants,
            current_participants=current_participants,
        )
