from discord.ui.select import Select
from discord import SelectOption
from typing import List, Optional
from discord import Interaction
import discord


class userMultiSelect(Select):
    _global_data = {}
    
    def __init__(
        self, 
        *, 
        custom_id: str = ..., 
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False, 
        row: Optional[int] = None,
        users : List[discord.User] = None,
        synckey : str = None,
    ) -> None:
        if synckey is not None:
            synckey = str(synckey).lower()
        
        if users is None and synckey is None:
            raise ValueError("Either users or synckey must be provided")
        
        if users is None and synckey not in self.__class__._global_data:
            raise ValueError("Synckey not found in global data")
        
        if users is not None:
            user_options = []
            for user in users:
                user_options.append(SelectOption(label=user.name, value=user.id))
        
            if synckey is not None:
                self.__class__._global_data[synckey] = users
        
        if users is None and synckey in self.__class__._global_data:
            user_options = self.__class__._global_data[synckey]

        super().__init__(
            custom_id=custom_id, 
            placeholder=placeholder, 
            disabled=disabled, 
            row=row, 
            options=user_options,
            min_values=min_values,
            max_values=max_values,
        )
