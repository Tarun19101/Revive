import re
from datetime import date, datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from schedule.models import ScheduleSlot, WeekSchedule
from tasks.models import Task

WEDNESDAY_10_30 = datetime(2026, 10, 14, 10, 30)
WEDNESDAY_23_30 = datetime(2026, 10, 14, 23, 30)
SATURDAY_23_30 = datetime(2026, 10, 17, 23, 30)
THIS_WEEK = date(2026, 10, 11)


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')

    def get(self, moment=WEDNESDAY_10_30):
        with patch('dashboard.views.now', return_value=moment):
            return self.client.get(reverse('dashboard'))

    def plan(self, *slots, week=THIS_WEEK):
        schedule = WeekSchedule.objects.create(user=self.user, week_start=week)
        ScheduleSlot.objects.bulk_create(
            [ScheduleSlot(schedule=schedule, day=d, hour=h, text=t) for d, h, t in slots]
        )

    def test_renders_with_no_tasks_or_schedule(self):
        response = self.get()
        self.assertContains(response, 'No pending tasks.')
        self.assertContains(response, 'Nothing planned', count=2)

    def test_shows_the_scheduled_tasks_for_now_and_next_hour_only(self):
        self.plan((3, 8, 'Already past'), (3, 10, 'Happening now'), (3, 11, 'Coming up'),
                  (3, 15, 'Later today'), (4, 10, 'Tomorrow'))
        response = self.get()
        self.assertContains(response, 'Now: 10:00 am to 11:00 am')
        self.assertContains(response, 'Happening now')
        self.assertContains(response, 'Next: 11:00 am to 12:00 pm')
        self.assertContains(response, 'Coming up')
        for hidden in ('Already past', 'Later today', 'Tomorrow'):
            self.assertNotContains(response, hidden)

    def test_an_empty_current_hour_still_shows_the_next_one(self):
        self.plan((3, 11, 'Coming up'))
        response = self.get()
        self.assertContains(response, 'Coming up')
        self.assertContains(response, 'Nothing planned', count=1)

    def test_the_minute_does_not_matter_within_an_hour(self):
        self.plan((3, 10, 'Happening now'))
        for minute in (0, 28, 59):
            response = self.get(datetime(2026, 10, 14, 10, minute))
            self.assertContains(response, 'Happening now')

    def test_after_11pm_the_next_hour_is_the_next_day(self):
        self.plan((3, 23, 'Late work'), (4, 0, 'After midnight'))
        response = self.get(WEDNESDAY_23_30)
        self.assertContains(response, 'Now: 11:00 pm to 12:00 am')
        self.assertContains(response, 'Late work')
        self.assertContains(response, 'Next: 12:00 am to 1:00 am')
        self.assertContains(response, 'After midnight')

    def test_saturday_night_next_hour_belongs_to_next_week(self):
        self.plan((6, 23, 'Last hour'), (0, 0, 'Not this week\'s Sunday'))
        response = self.get(SATURDAY_23_30)
        self.assertContains(response, 'Last hour')
        self.assertNotContains(response, "Not this week")
        self.assertContains(response, 'Nothing planned', count=1)

    def test_other_players_plans_are_not_shown(self):
        other = User.objects.create_user('rival', password='pw')
        schedule = WeekSchedule.objects.create(user=other, week_start=THIS_WEEK)
        ScheduleSlot.objects.create(schedule=schedule, day=3, hour=10, text='Rival secret')
        self.assertNotContains(self.get(), 'Rival secret')

    def test_shows_up_to_five_tasks_and_counts_the_rest(self):
        for i in range(7):
            Task.objects.create(user=self.user, title=f'task {i}')
        self.assertContains(self.get(), '+2 more')

    def test_events_are_gone(self):
        self.assertNotContains(self.get(), 'Events')


class DashboardClockTests(TestCase):
    """The page title shows the current date and time as dd-mm-yyyy ::: day ::: hh:mm am/pm."""

    def setUp(self):
        User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')

    def page(self, moment):
        with patch('config.context_processors.now', return_value=moment):
            return self.client.get(reverse('dashboard')).content.decode()

    def tab_title(self, moment):
        return re.search(r'<title>(.*?)</title>', self.page(moment), re.S).group(1)

    def test_tab_title_is_plain_text_in_the_format(self):
        self.assertEqual(self.tab_title(datetime(2026, 10, 16, 16, 28)), '16-10-2026 ::: Friday ::: 04:28 pm')

    def test_same_text_is_shown_in_the_page(self):
        html = self.page(datetime(2026, 10, 16, 16, 28))
        self.assertIn('>16-10-2026 ::: Friday ::: 04:28 pm</p>', html)

    def test_username_no_longer_replaces_it(self):
        self.assertNotIn('<title>player</title>', self.page(datetime(2026, 10, 16, 16, 28)))

    def test_card_title_is_back_to_now_and_next(self):
        self.assertIn('Now &amp; Next</h3>', self.page(datetime(2026, 10, 16, 16, 28)))

    def test_morning_keeps_the_leading_zero(self):
        self.assertEqual(self.tab_title(datetime(2026, 10, 16, 9, 5)), '16-10-2026 ::: Friday ::: 09:05 am')

    def test_noon_is_12_pm(self):
        self.assertEqual(self.tab_title(datetime(2026, 10, 16, 12, 0)), '16-10-2026 ::: Friday ::: 12:00 pm')

    def test_just_after_midnight_is_12_am_of_the_new_day(self):
        self.assertEqual(self.tab_title(datetime(2026, 10, 17, 0, 30)), '17-10-2026 ::: Saturday ::: 12:30 am')

    def test_day_and_month_are_day_first_with_two_digits(self):
        self.assertEqual(self.tab_title(datetime(2026, 1, 3, 23, 59)), '03-01-2026 ::: Saturday ::: 11:59 pm')