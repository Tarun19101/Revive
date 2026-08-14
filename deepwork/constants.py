# Python's date.weekday(): Monday=0 ... Sunday=6
DAY_SKILLS = {
    0: ['mathematician'],                    # Monday
    1: ['battle_iq', 'dr_doctor'],            # Tuesday
    2: ['devils_advocate'],                   # Wednesday
    3: ['master_mind', 'power_house'],        # Thursday
    4: ['tech_expert'],                       # Friday
    5: ['weapon_mastery', 'hobby'],     # Saturday
    6: ['silver_tongue', 'walking_library'],  # Sunday
}

TRAINING_XP = 20

TRAINING_GUIDES = {
    'mathematician': {
        'insight': [
            'Learn 1-30 multiplication tables and squares',
            'Master shortcuts for addition, subtraction, multiplication, division',
            'Study fractions, percentages, and basic algebra',
            'Learn mental math tricks and vedic math techniques',
        ],
        'practice': [
            'Play card games and dice games requiring mental calculation',
            'Practice magic tricks like Doomsday Rule for calendar calculations',
            'Solve Sudoku, Kakuro, and number puzzles daily',
            'Mental math competitions or timed calculation challenges',
        ]
    },
    'battle_iq': {
        'insight': [
            'Study chess openings, middle game tactics, and endgames',
            'Learn martial arts fundamentals and defensive strategies',
            'Study game theory and decision-making under pressure',
            'Watch instructional videos on pattern recognition',
        ],
        'practice': [
            'Play chess online (blitz, rapid, classical)',
            'Spar with a martial arts partner or trainer',
            'Play strategy games (Risk, Civilization, Go)',
            'Analyze your losses and study opponent patterns',
        ]
    },
    'weapon_mastery': {
        'insight': [
            'Study weapon history and mechanics (sword, bow, etc)',
            'Learn proper grip, stance, and body mechanics',
            'Study distance, timing, and angle principles',
            'Learn safety protocols and form guidelines',
        ],
        'practice': [
            'Regular training at a weapon club or dojo',
            'Practice forms and katas repeatedly',
            'Spar with experienced practitioners',
            'Participate in tournaments or friendly competitions',
        ]
    },
    'walking_library': {
        'insight': [
            'Read books across different genres and subjects',
            'Study history, philosophy, science, and literature',
            'Learn etymology and how language evolves',
            'Explore interconnections between different fields',
        ],
        'practice': [
            'Teach others what you\'ve learned',
            'Write summaries or reviews of books',
            'Join book clubs and discuss ideas',
            'Create concept maps linking knowledge across domains',
        ]
    },
    'tech_expert': {
        'insight': [
            'Learn programming languages and frameworks',
            'Study computer science fundamentals (algorithms, data structures)',
            'Keep up with tech news and new tools',
            'Understand system design and architecture patterns',
        ],
        'practice': [
            'Build projects from scratch (web apps, games, tools)',
            'Contribute to open-source projects',
            'Solve coding challenges on platforms like LeetCode',
            'Teach or mentor others in programming',
        ]
    },
    'power_house': {
        'insight': [
            'Learn exercise physiology and proper form',
            'Study nutrition and recovery principles',
            'Learn progressive overload and periodization',
            'Understand muscle groups and biomechanics',
        ],
        'practice': [
            'Lift weights consistently with progressive resistance',
            'Train with a strength coach for form feedback',
            'Participate in strength competitions or challenges',
            'Track progress with measurable metrics (1RM, endurance)',
        ]
    },
    'dr_doctor': {
        'insight': [
            'Study human anatomy and physiology',
            'Learn first aid and emergency response',
            'Study nutrition and wellness principles',
            'Learn common illnesses and prevention strategies',
        ],
        'practice': [
            'Volunteer at hospitals or health clinics',
            'Practice CPR and first aid certifications',
            'Help friends/family with health concerns',
            'Participate in health awareness campaigns',
        ]
    },
    'devils_advocate': {
        'insight': [
            'Study logic, fallacies, and argumentation',
            'Learn debate frameworks and rhetoric',
            'Study different philosophical and political perspectives',
            'Learn to identify cognitive biases',
        ],
        'practice': [
            'Participate in debate competitions or clubs',
            'Argue different sides of controversial topics',
            'Challenge your own beliefs regularly',
            'Discuss complex ideas with smart people who disagree',
        ]
    },
    'master_mind': {
        'insight': [
            'Study productivity systems and time management',
            'Learn focus techniques (Pomodoro, deep work, etc)',
            'Study goal-setting and strategic planning',
            'Learn psychology of motivation and habits',
        ],
        'practice': [
            'Plan and execute long-term projects',
            'Use productivity tools and track your output',
            'Mentor others on organization and planning',
            'Reflect daily on what worked and what didn\'t',
        ]
    },
    'silver_tongue': {
        'insight': [
            'Study communication and persuasion principles',
            'Learn body language and non-verbal communication',
            'Study storytelling and narrative techniques',
            'Learn to read people and emotional intelligence',
        ],
        'practice': [
            'Give presentations or talks regularly',
            'Network at social events and practice mingling',
            'Lead meetings or group discussions',
            'Record yourself speaking and review for improvement',
        ]
    },
    'hobby': {
        'insight': [
            'Study cooking techniques and food science',
            'Learn flavor combinations and recipe structure',
            'Study different cuisines and their philosophies',
            'Learn nutrition and dietary principles',
        ],
        'practice': [
            'Cook new recipes and experiment with flavors',
            'Cook for others and get feedback',
            'Participate in cooking competitions',
            'Master one cuisine deeply before exploring others',
        ]
    },
}