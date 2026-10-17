from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .constants import ATTRIBUTE_SKILLS, ATTRIBUTES, SKILL_CATALOG, UTC_OFFSETS, utc_label
from .models import PlayerSkill, get_attribute_levels

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



class UtcOffsetListTests(TestCase):
    def test_labels(self):
        self.assertEqual(utc_label(330), 'UTC+05:30')
        self.assertEqual(utc_label(345), 'UTC+05:45')
        self.assertEqual(utc_label(-570), 'UTC-09:30')
        self.assertEqual(utc_label(0), 'UTC+00:00')
        self.assertEqual(utc_label(-720), 'UTC-12:00')
        self.assertEqual(utc_label(840), 'UTC+14:00')

    def test_list_is_sorted_unique_and_runs_from_minus_12_to_plus_14(self):
        self.assertEqual(UTC_OFFSETS, sorted(set(UTC_OFFSETS)))
        self.assertEqual((UTC_OFFSETS[0], UTC_OFFSETS[-1]), (-720, 840))


def machine_offset(minutes):
    """Pretend this computer's clock is set to the given UTC offset."""
    fake = patch('accounts.views.datetime')

    class Context:
        def __enter__(self):
            mock = fake.start()
            mock.now.return_value.astimezone.return_value.utcoffset.return_value = timedelta(minutes=minutes)
            return mock

        def __exit__(self, *exc):
            fake.stop()

    return Context()


class OnboardingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')
        self.url = reverse('onboarding')
        self.valid = {'date_of_birth': '2000-05-05', 'weight_kg': '70',
                      'height_cm': '175', 'utc_offset_minutes': '330'}

    def profile(self):
        profile = self.user.profile
        profile.refresh_from_db()
        return profile

    def test_asks_dob_weight_height_and_time_zone_only(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['form'].fields),
                         ['date_of_birth', 'weight_kg', 'height_cm', 'utc_offset_minutes'])
        for old_question in ('martial_art', 'weapon', 'hobby'):
            self.assertNotContains(response, f'name="{old_question}"')
        self.assertContains(response, 'Time zone (UTC offset)')
        self.assertContains(response, 'UTC+05:30')

    def test_saving_stores_all_four_answers_and_completes_onboarding(self):
        response = self.client.post(self.url, self.valid)
        self.assertRedirects(response, reverse('dashboard'))
        profile = self.profile()
        self.assertEqual(profile.date_of_birth, date(2000, 5, 5))
        self.assertEqual((float(profile.weight_kg), float(profile.height_cm)), (70.0, 175.0))
        self.assertEqual(profile.utc_offset_minutes, 330)
        self.assertTrue(profile.onboarding_complete)

    def test_utc_plus_zero_counts_as_an_answer(self):
        self.client.post(self.url, {**self.valid, 'utc_offset_minutes': '0'})
        profile = self.profile()
        self.assertEqual(profile.utc_offset_minutes, 0)
        self.assertTrue(profile.onboarding_complete)

    def test_negative_offsets_work(self):
        self.client.post(self.url, {**self.valid, 'utc_offset_minutes': '-570'})
        self.assertEqual(self.profile().utc_offset_minutes, -570)

    def test_time_zone_is_required(self):
        response = self.client.post(self.url, {**self.valid, 'utc_offset_minutes': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn('utc_offset_minutes', response.context['form'].errors)
        self.assertIsNone(self.profile().utc_offset_minutes)
        self.assertFalse(self.profile().onboarding_complete)

    def test_an_offset_that_is_not_in_the_list_is_rejected(self):
        for bad in ('333', '99999', 'abc'):
            with self.subTest(offset=bad):
                response = self.client.post(self.url, {**self.valid, 'utc_offset_minutes': bad})
                self.assertIn('utc_offset_minutes', response.context['form'].errors)
                self.assertIsNone(self.profile().utc_offset_minutes)

    def test_the_other_answers_are_still_required(self):
        for missing in ('date_of_birth', 'weight_kg', 'height_cm'):
            with self.subTest(missing=missing):
                response = self.client.post(self.url, {**self.valid, missing: ''})
                self.assertIn(missing, response.context['form'].errors)

    def test_finished_players_are_sent_to_the_dashboard(self):
        self.client.post(self.url, self.valid)
        self.assertRedirects(self.client.get(self.url), reverse('dashboard'))

    def test_a_profile_without_a_time_zone_is_not_complete(self):
        profile = self.user.profile
        profile.date_of_birth, profile.weight_kg, profile.height_cm = date(2000, 1, 1), 70, 175
        profile.save()
        self.assertFalse(profile.onboarding_complete)

    def test_this_computers_offset_is_preselected(self):
        with machine_offset(330):
            response = self.client.get(self.url)
        self.assertEqual(response.context['form'].initial['utc_offset_minutes'], 330)
        self.assertContains(response, '<option value="330" selected>UTC+05:30</option>')

    def test_an_offset_nobody_uses_is_not_preselected(self):
        with machine_offset(320):
            response = self.client.get(self.url)
        self.assertIsNone(response.context['form'].initial['utc_offset_minutes'])

    def test_an_offset_the_player_already_chose_is_not_overridden(self):
        profile = self.user.profile
        profile.utc_offset_minutes = 60
        profile.save()
        with machine_offset(330):
            response = self.client.get(self.url)
        self.assertEqual(response.context['form'].initial['utc_offset_minutes'], 60)


class ProfileTimeZoneTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        profile = self.user.profile
        profile.date_of_birth, profile.weight_kg, profile.height_cm = date(2000, 5, 5), 70, 175
        profile.utc_offset_minutes = 330
        profile.save()
        self.client.login(username='player', password='pw')
        self.url = reverse('profile')

    def save_profile(self, **changes):
        data = {'profile_submit': '1', 'weight_kg': '70', 'height_cm': '175', 'utc_offset_minutes': '330'}
        return self.client.post(self.url, {**data, **changes})

    def test_profile_form_offers_weight_height_and_time_zone(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['form'].fields), ['weight_kg', 'height_cm', 'utc_offset_minutes'])

    def test_changing_the_time_zone_and_weight(self):
        response = self.save_profile(utc_offset_minutes='-300', weight_kg='71')
        self.assertRedirects(response, self.url)
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.utc_offset_minutes, -300)
        self.assertEqual(float(profile.weight_kg), 71.0)

    def test_an_invalid_offset_is_not_saved(self):
        response = self.save_profile(utc_offset_minutes='1')
        self.assertEqual(response.status_code, 200)
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.utc_offset_minutes, 330)

    def test_a_player_who_never_chose_one_gets_this_computers_offset_suggested(self):
        profile = self.user.profile
        profile.utc_offset_minutes = None
        profile.save()
        with machine_offset(540):
            response = self.client.get(self.url)
        self.assertEqual(response.context['form'].initial['utc_offset_minutes'], 540)


class SkillChoiceRemovedTests(TestCase):
    def test_skills_no_longer_store_a_martial_art_weapon_or_hobby(self):
        self.assertNotIn('choice', [field.name for field in PlayerSkill._meta.get_fields()])

    def test_progress_page_shows_plain_skill_names(self):
        user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')
        response = self.client.get(reverse('progress'))
        for skill in SKILL_CATALOG.values():
            self.assertContains(response, skill['name'])