from discordPyExt import EmbedX, EmbedFactory
import typing

coop_banner_embedf = EmbedFactory(
    title="[COOP] {name}",
    color=0x00ff00,
    description="{notes}"
).field(
    name="Coordinator",
    value="{coordinator}",
).field(
    name="Role",
    value="{role}",
    inline=True
).field(
    name="Current Participants ({current_count}/{max_participants}){overflow}",
    value=">{current_participants}",
    inline=False
)

coop_thread_meta = "{current_count} out of {max_participants} [{overflow}]"

# TOF Gates
booster_frame_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/3/3d/Icon_Item_Booster_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160142"
booster_frame_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/6/6e/Icon_Item_Booster_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160143"
nano_coating_1 =  "https://static.wikia.nocookie.net/toweroffantasy/images/7/79/Icon_Item_Nano_Coating_I.png/revision/latest/scale-to-width-down/80?cb=20220819160147"
nano_coating_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/c/cc/Icon_Item_Nano_Coating_II.png/revision/latest/scale-to-width-down/80?cb=20220819160149"
nanofiber_1 ="https://static.wikia.nocookie.net/toweroffantasy/images/5/56/Icon_Item_Nanofiber_Frame_I.png/revision/latest/scale-to-width-down/80?cb=20220819160153"
nanofiber_2 ="https://static.wikia.nocookie.net/toweroffantasy/images/8/8d/Icon_Item_Nanofiber_Frame_II.png/revision/latest/scale-to-width-down/80?cb=20220819160155"
acidproof_1 = "https://static.wikia.nocookie.net/toweroffantasy/images/b/b0/Icon_Item_Acidproof_Glaze_I.png/revision/latest/scale-to-width-down/80?cb=20220819160136"
acidproof_2 = "https://static.wikia.nocookie.net/toweroffantasy/images/8/83/Icon_Item_Acidproof_Glaze_II.png/revision/latest/scale-to-width-down/80?cb=20220819160138"

# TOF material embed factories
booster_frame_embedf2 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=booster_frame_2,
)

nano_coating_embedf2 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=nano_coating_2,
)

nanofiber_embedf2 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=nanofiber_2,
)

acidproof_embedf2 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=acidproof_2,
)

#
booster_frame_embedf1 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=booster_frame_1,
)

nano_coating_embedf1 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=nano_coating_1,
)

nanofiber_embedf1 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=nanofiber_1,
)

acidproof_embedf1 = coop_banner_embedf.inherit(
    title="{name}",
    thumbnail=acidproof_1,
)
