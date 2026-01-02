
ISA_SECTIONS = {
    "ISA_100x100x8": {
        "leg_h": 100,
        "leg_w": 100,
        "thickness": 8
    },
    "ISA_90x60x6": {
        "leg_h": 90,
        "leg_w": 60,
        "thickness": 6
    },
    "ISA_75x75x6": {
        "leg_h": 75,
        "leg_w": 75,
        "thickness": 6
    }
}

CHANNEL_SECTIONS = {
    "ISMC_100": {
        "depth": 100,
        "flange_width": 50,
        "web_thickness": 5,
        "flange_thickness": 7
    },
    "ISMC_125": {
        "depth": 125,
        "flange_width": 65,
        "web_thickness": 5.3,
        "flange_thickness": 8
    },
    "ISMC_150": {
        "depth": 150,
        "flange_width": 75,
        "web_thickness": 5.7,
        "flange_thickness": 8.5
    }
}


SECTION_DATABASE = {
    "ANGLE": ISA_SECTIONS,
    "CHANNEL": CHANNEL_SECTIONS
}


def get_section_props(section_type, designation):
    """
    Returns section properties dict based on section type and designation.
    """
    if section_type not in SECTION_DATABASE:
        raise ValueError(
            f"Unsupported section type '{section_type}'. "
            f"Available: {list(SECTION_DATABASE.keys())}"
        )

    db = SECTION_DATABASE[section_type]

    if designation not in db:
        raise ValueError(
            f"Invalid designation '{designation}' for section type '{section_type}'. "
            f"Available: {list(db.keys())}"
        )

    return db[designation]


SECTION_ROLL_RULES = {
    "ANGLE": {
        "diagonal": [1.5708, -1.5708],   # ±90°
        "horizontal": [2*1.5708]              # 0°
    },
    "CHANNEL": {
        "diagonal": [0],   # ±90°
        "horizontal": [2*1.5708]              # 180°
    }
}


def get_section_roll_angle(
    section_type,
    member_role,
    roll_sign=+1
):
    """
    Returns roll angle based on:
    - section type (ANGLE / CHANNEL)
    - member role (diagonal / horizontal)
    - roll sign (+1 / -1)
    """

    rules = SECTION_ROLL_RULES.get(section_type)
    if not rules:
        return 0.0  # BOX, I-section, etc.

    allowed = rules.get(member_role, [0.0])

    if len(allowed) == 1:
        return allowed[0]

    # multiple allowed rolls (±90)
    return max(allowed) if roll_sign > 0 else min(allowed)
