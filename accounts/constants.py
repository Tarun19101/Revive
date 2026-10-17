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