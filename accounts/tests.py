from django.contrib.auth.models import User
from django.test import TestCase

from .constants import ATTRIBUTE_SKILLS, ATTRIBUTES, SKILL_CATALOG
from .models import get_attribute_levels


class CatalogTests(TestCase):
    def test_there_are_five_attributes_in_order(self):
        self.assertEqual(list(ATTRIBUTES.values()), ['Power', 'Intelligence', 'Charisma', 'Wisdom', 'Luck'])

    def test_there_are_six_skills_under_the_right_attributes(self):
        self.assertEqual(
            {key: (skill['name'], skill['attribute']) for key, skill in SKILL_CATALOG.items()},
            {
                'battle_iq': ('Battle IQ', 'power'),
                'body_aptitude': ('Body Aptitude', 'power'),
                'walking_library': ('Walking Library', 'intelligence'),
                'artist': ('Artist', 'charisma'),
                'master_mind': ('Master Mind', 'wisdom'),
                'magician': ('Magician', 'luck'),
            },
        )

    def test_every_skill_belongs_to_exactly_one_known_attribute(self):
        listed = [key for keys in ATTRIBUTE_SKILLS.values() for key in keys]
        self.assertCountEqual(listed, SKILL_CATALOG.keys())
        self.assertEqual(list(ATTRIBUTE_SKILLS), list(ATTRIBUTES))

    def test_power_has_two_skills_and_the_rest_have_one(self):
        self.assertEqual(
            {attr: len(keys) for attr, keys in ATTRIBUTE_SKILLS.items()},
            {'power': 2, 'intelligence': 1, 'charisma': 1, 'wisdom': 1, 'luck': 1},
        )


class NewPlayerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')

    def test_new_player_gets_all_six_skills_at_level_zero(self):
        skills = self.user.skills.all()
        self.assertCountEqual([s.skill_key for s in skills], SKILL_CATALOG.keys())
        self.assertTrue(all((s.level, s.xp) == (0, 0) for s in skills))

    def test_all_attributes_start_at_level_zero(self):
        levels = get_attribute_levels(self.user)
        self.assertEqual(list(levels), list(ATTRIBUTES))
        self.assertTrue(all(attr['level'] == 0 for attr in levels.values()))


class SkillXpTests(TestCase):
    def setUp(self):
        self.skill = User.objects.create_user('player', password='pw').skills.get(skill_key='battle_iq')

    def test_reaching_level_n_costs_n_times_100(self):
        costs = []
        for level in range(4):
            self.skill.level = level
            costs.append(self.skill.xp_for_next_level)
        self.assertEqual(costs, [100, 200, 300, 400])

    def test_just_under_the_cost_does_not_level_up(self):
        self.assertEqual(self.skill.add_xp(99), 0)
        self.assertEqual((self.skill.level, self.skill.xp), (0, 99))

    def test_exactly_the_cost_levels_up_with_nothing_left(self):
        self.assertEqual(self.skill.add_xp(100), 1)
        self.assertEqual((self.skill.level, self.skill.xp), (1, 0))

    def test_a_big_gain_can_pass_several_levels(self):
        # 350 XP: 100 for level 1, 200 for level 2, 50 left over.
        self.assertEqual(self.skill.add_xp(350), 2)
        self.assertEqual((self.skill.level, self.skill.xp), (2, 50))

    def test_xp_carries_over_between_gains(self):
        self.skill.add_xp(90)
        self.skill.add_xp(20)
        self.assertEqual((self.skill.level, self.skill.xp), (1, 10))

    def test_the_result_is_saved(self):
        self.skill.add_xp(130)
        self.skill.refresh_from_db()
        self.assertEqual((self.skill.level, self.skill.xp), (1, 30))


class AttributeLevelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')

    def set_level(self, key, level):
        self.user.skills.filter(skill_key=key).update(level=level)

    def test_power_is_the_average_of_its_two_skills_rounded_down(self):
        self.set_level('battle_iq', 3)
        self.set_level('body_aptitude', 2)
        self.assertEqual(get_attribute_levels(self.user)['power']['level'], 2)   # (3 + 2) // 2

    def test_power_with_one_trained_skill_is_half_of_it_rounded_down(self):
        self.set_level('battle_iq', 5)
        self.assertEqual(get_attribute_levels(self.user)['power']['level'], 2)   # (5 + 0) // 2

    def test_single_skill_attributes_equal_their_skill(self):
        for skill_key, attribute in [('walking_library', 'intelligence'), ('artist', 'charisma'),
                                     ('master_mind', 'wisdom'), ('magician', 'luck')]:
            self.set_level(skill_key, 4)
            self.assertEqual(get_attribute_levels(self.user)[attribute]['level'], 4)