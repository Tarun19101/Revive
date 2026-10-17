from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .constants import HABIT_CATALOG
from .models import PlayerHabit


class HabitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')

    def habit(self, habit_key):
        return PlayerHabit.objects.get(user=self.user, habit_key=habit_key)

    def complete(self, habit_key):
        return self.client.post(reverse('complete_habit', args=[self.habit(habit_key).id]), follow=True)

    def skill_state(self):
        return sorted(self.user.skills.values_list('skill_key', 'level', 'xp'))

    def test_habits_are_not_connected_to_skills(self):
        for habit_key, habit in HABIT_CATALOG.items():
            with self.subTest(habit=habit_key):
                self.assertEqual(list(habit), ['name'])

    def test_completing_a_habit_gives_2_player_xp_and_never_touches_skills(self):
        skills_before = self.skill_state()
        for number, habit_key in enumerate(HABIT_CATALOG, start=1):
            with self.subTest(habit=habit_key):
                response = self.complete(habit_key)
                self.assertEqual(response.status_code, 200)
                self.user.profile.refresh_from_db()
                self.assertEqual(self.user.profile.xp, 2 * number)
        self.assertEqual(self.skill_state(), skills_before)

    def test_the_message_mentions_player_xp_only(self):
        response = self.complete('workout')
        self.assertContains(response, 'Workout done! +2 player XP')
        self.assertNotContains(response, 'Battle IQ')

    def test_completing_twice_in_a_day_pays_once(self):
        self.complete('read_books')
        self.complete('read_books')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp, 2)

    def test_player_xp_rolls_over_into_the_next_level(self):
        profile = self.user.profile
        profile.level, profile.xp = 1, 49          # level 1 needs 50
        profile.save()
        self.complete('workout')
        profile.refresh_from_db()
        self.assertEqual((profile.level, profile.xp), (2, 1))

    def test_streak_grows_when_done_on_consecutive_days(self):
        habit = self.habit('meditate')
        habit.streak, habit.last_completed = 3, date.today() - timedelta(days=1)
        habit.save()
        self.complete('meditate')
        habit.refresh_from_db()
        self.assertEqual((habit.streak, habit.longest_streak), (4, 4))

    def test_streak_restarts_after_a_missed_day(self):
        habit = self.habit('meditate')
        habit.streak, habit.longest_streak = 6, 6
        habit.last_completed = date.today() - timedelta(days=3)
        habit.save()
        self.complete('meditate')
        habit.refresh_from_db()
        self.assertEqual((habit.streak, habit.longest_streak), (1, 6))

    def test_cannot_complete_someone_elses_habit(self):
        other = User.objects.create_user('rival', password='pw')
        theirs = PlayerHabit.objects.get(user=other, habit_key='workout')
        response = self.client.post(reverse('complete_habit', args=[theirs.id]))
        self.assertEqual(response.status_code, 404)