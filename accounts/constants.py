ATTRIBUTES = {
    'power': 'Power',
    'intelligence': 'Intelligence',
    'charisma': 'Charisma',
    'wisdom': 'Wisdom',
    'luck': 'Luck',
}

# skill_key -> config
SKILL_CATALOG = {
    'battle_iq':       {'name': 'Battle IQ',       'attribute': 'power'},
    'body_aptitude':   {'name': 'Body Aptitude',   'attribute': 'power'},
    'walking_library': {'name': 'Walking Library', 'attribute': 'intelligence'},
    'artist':          {'name': 'Artist',          'attribute': 'charisma'},
    'master_mind':     {'name': 'Master Mind',     'attribute': 'wisdom'},
    'magician':        {'name': 'Magician',        'attribute': 'luck'},
}

# attribute -> list of skill_keys under it (built from SKILL_CATALOG so the two can't disagree)
ATTRIBUTE_SKILLS = {
    attr_key: [key for key, skill in SKILL_CATALOG.items() if skill['attribute'] == attr_key]
    for attr_key in ATTRIBUTES
}

# Still used by the onboarding form until Step B removes it.
# UTC offsets in use around the world, in minutes (330 = UTC+05:30).
UTC_OFFSETS = [
    -720, -660, -600, -570, -540, -480, -420, -360, -300, -240, -210, -180, -120, -60,
    0, 60, 120, 180, 210, 240, 270, 300, 330, 345, 360, 390, 420, 480, 525, 540, 570,
    600, 630, 660, 720, 765, 780, 840,
]


def utc_label(minutes):
    """330 -> 'UTC+05:30', -570 -> 'UTC-09:30', 0 -> 'UTC+00:00'."""
    sign = '+' if minutes >= 0 else '-'
    hours, mins = divmod(abs(minutes), 60)
    return f"UTC{sign}{hours:02d}:{mins:02d}"


UTC_OFFSET_CHOICES = [(minutes, utc_label(minutes)) for minutes in UTC_OFFSETS]