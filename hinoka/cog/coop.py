import typing

PARTICIPANTS_OPTIONS = typing.Literal[
    "No Limit", "3", "4", "5", "6", "7", "8"
]

COOP_PRESETS = typing.Literal[
    "TOF 4 man misc",
    "TOF 8 man misc",
    "TOF Raid",
    "TOF Joint Operation",
    "Honkai COOP",
]

COOP_PRESETS_META = {
    "TOF 4 man misc": {
        "name" : "TOF Party",
        "max_participants" : 4,
    },
    "TOF 8 man misc" : {
        "name" : "TOF Party",
        "max_participants" : 8,
    },
    "TOF Raid" : {
        "name" : "TOF Raid",
        "max_participants" : 8,
    },
    "TOF Joint Operation" : {
        "name" : "TOF JO",
        "max_participants" : 4,
    },
    "Honkai COOP" : {
        "name" : "Honkai COOP",
        "max_participants" : 3,
    },
}

MATERIAL_TYPES = typing.Literal["Booster Frame", "Nano Coating", "Nanofiber Frame", "Acidproof Glaze"] 