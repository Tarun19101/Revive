ATTRIBUTES = {
    'strength': 'Strength',
    'intelligence': 'Intelligence',
    'endurance': 'Endurance',
    'wisdom': 'Wisdom',
    'charisma': 'Charisma',
    'luck': 'Luck',
}

# skill_key -> config
SKILL_CATALOG = {
    'battle_iq':        {'name': 'Battle IQ',        'attribute': 'strength',     'choice_type': 'martial_art'},
    'weapon_mastery':   {'name': 'Weapon Mastery',    'attribute': 'strength',     'choice_type': 'weapon'},
    'walking_library':  {'name': 'Walking Library',   'attribute': 'intelligence', 'choice_type': None},
    'tech_expert':      {'name': 'Tech Expert',       'attribute': 'intelligence', 'choice_type': None},
    'power_house':      {'name': 'Power-House',       'attribute': 'endurance',    'choice_type': None},
    'dr_doctor':        {'name': 'Dr. Doctor',        'attribute': 'endurance',    'choice_type': None},
    'devils_advocate':  {'name': "Devil's Advocate",  'attribute': 'wisdom',       'choice_type': None},
    'master_mind':      {'name': 'Master-Mind',       'attribute': 'wisdom',       'choice_type': None},
    'silver_tongue':    {'name': 'Silver Tongue',     'attribute': 'charisma',     'choice_type': None},
    'hobby':      {'name': 'Hobby',       'attribute': 'charisma',     'choice_type': 'hobby'},
    'mathematician':    {'name': 'Mathematician',     'attribute': 'luck',         'choice_type': None},
}

# attribute -> list of skill_keys under it
ATTRIBUTE_SKILLS = {
    'strength': ['battle_iq', 'weapon_mastery'],
    'intelligence': ['walking_library', 'tech_expert'],
    'endurance': ['power_house', 'dr_doctor'],
    'wisdom': ['devils_advocate', 'master_mind'],
    'charisma': ['silver_tongue', 'hobby'],
    'luck': ['mathematician'],
}

CHOICE_OPTIONS = {
    'martial_art': [
        'Boxing', 'Karate', 'Judo', 'Brazilian Jiu-Jitsu', 'Muay Thai',
        'Taekwondo', 'Wrestling', 'Kung Fu', 'Krav Maga', 'Aikido', 'Jeet Kune Do',
    ],
    'weapon': [
        'Sword', 'Bow', 'Guns'
        'Spear', 'Dagger', 'Axe', 'Mace', 'Hammer',
        'Nunchaku', 'Whip',
    ],
    'hobby': [
        'Cooking', 'Drawing', 'Painting', 'Dancing', 'Singing',
        'Photography', 'Writing', 'Sculpting', 'Pottery', 'Playing an Instrument',
    ],
}