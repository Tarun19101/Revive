from datetime import date, datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import ScheduleSlot, WeekSchedule
from .utils import day_index, hour_label, week_start

# 2026-10-11 is a Sunday.
SUNDAY = datetime(2026, 10, 11, 9, 0)
WEDNESDAY = datetime(2026, 10, 14, 10, 30)
SATURDAY_LATE = datetime(2026, 10, 17, 23, 59)
NEXT_SUNDAY = datetime(2026, 10, 18, 0, 5)


def at(moment):
    return patch('schedule.views.now', return_value=moment)


class TimeHelperTests(TestCase):
    def test_week_start_is_the_sunday_on_or_before(self):
        self.assertEqual(week_start(date(2026, 10, 11)), date(2026, 10, 11))  # Sunday
        self.assertEqual(week_start(date(2026, 10, 12)), date(2026, 10, 11))  # Monday
        self.assertEqual(week_start(date(2026, 10, 14)), date(2026, 10, 11))  # Wednesday
        self.assertEqual(week_start(date(2026, 10, 17)), date(2026, 10, 11))  # Saturday
        self.assertEqual(week_start(date(2026, 10, 18)), date(2026, 10, 18))  # next Sunday

    def test_week_start_crosses_month_and_year(self):
        self.assertEqual(week_start(date(2027, 1, 1)), date(2026, 12, 27))

    def test_day_index_runs_sunday_to_saturday(self):
        self.assertEqual([day_index(date(2026, 10, 11 + i)) for i in range(7)], [0, 1, 2, 3, 4, 5, 6])

    def test_hour_labels(self):
        self.assertEqual(hour_label(0), '12:00 am to 1:00 am')
        self.assertEqual(hour_label(11), '11:00 am to 12:00 pm')
        self.assertEqual(hour_label(12), '12:00 pm to 1:00 pm')
        self.assertEqual(hour_label(23), '11:00 pm to 12:00 am')


class ScheduleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')
        self.url = reverse('schedule')
        self.create_url = reverse('schedule_create')

    def test_login_required(self):
        self.client.logout()
        for url in (self.url, self.create_url):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response['Location'])

    def test_form_has_every_hour_of_every_day(self):
        with at(WEDNESDAY):
            response = self.client.get(self.url)
        html = response.content.decode()
        self.assertEqual(html.count('name="slot_'), 7 * 24)
        self.assertIn('name="slot_0_0"', html)
        self.assertIn('name="slot_6_23"', html)
        self.assertIn('12:00 am to 1:00 am', html)
        self.assertIn('11:00 pm to 12:00 am', html)
        for short in ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'):
            self.assertContains(response, f'>{short}</button>')

    def test_create_button_enabled_when_week_has_no_schedule(self):
        with at(WEDNESDAY):
            response = self.client.get(self.url)
        self.assertFalse(response.context['schedule'])
        self.assertNotContains(response, 'disabled>')

    def test_saving_stores_only_filled_hours_and_strips_text(self):
        with at(WEDNESDAY):
            response = self.client.post(self.create_url, {
                'slot_0_0': '  Sleep  ',
                'slot_0_1': '',
                'slot_3_14': 'Deep work',
                'slot_6_23': 'Wind down',
            })
        self.assertRedirects(response, self.url)
        schedule = WeekSchedule.objects.get()
        self.assertEqual(schedule.user, self.user)
        self.assertEqual(schedule.week_start, date(2026, 10, 11))
        self.assertEqual(
            list(schedule.slots.values_list('day', 'hour', 'text')),
            [(0, 0, 'Sleep'), (3, 14, 'Deep work'), (6, 23, 'Wind down')],
        )

    def test_saved_week_is_shown_and_button_is_disabled(self):
        with at(WEDNESDAY):
            self.client.post(self.create_url, {'slot_3_10': 'Write report', 'slot_0_8': 'Plan week'})
            response = self.client.get(self.url)
        html = response.content.decode()
        self.assertContains(response, 'Write report')
        self.assertContains(response, 'Plan week')
        self.assertRegex(html, r'id="create-schedule-btn"[^>]*\sdisabled')
        self.assertContains(response, 'Sunday, 18 Oct')  # when the button comes back
        self.assertNotContains(response, 'id="schedule-editor"')
        self.assertEqual(response.context['today_index'], 3)  # opens on Wednesday

    def test_current_hour_is_flagged_only_on_today(self):
        with at(WEDNESDAY):  # Wednesday 10:30 -> the 10:00 am hour
            self.client.post(self.create_url, {'slot_3_10': 'Focus', 'slot_2_10': 'Other day'})
            response = self.client.get(self.url)
        flagged = [
            (day['name'], row['label'])
            for day in response.context['view_days'] for row in day['rows'] if row['is_now']
        ]
        self.assertEqual(flagged, [('Wednesday', '10:00 am to 11:00 am')])
        self.assertContains(response, 'aria-current="time"', count=1)

    def test_second_save_in_the_same_week_is_rejected(self):
        with at(WEDNESDAY):
            self.client.post(self.create_url, {'slot_0_0': 'First'})
            response = self.client.post(self.create_url, {'slot_0_0': 'Second'}, follow=True)
        self.assertEqual(WeekSchedule.objects.count(), 1)
        self.assertEqual(ScheduleSlot.objects.get().text, 'First')
        self.assertContains(response, 'already created')

    def test_button_comes_back_on_the_next_sunday(self):
        with at(SATURDAY_LATE):
            self.client.post(self.create_url, {'slot_6_23': 'Last hour of the week'})
            self.assertTrue(self.client.get(self.url).context['schedule'])
        with at(NEXT_SUNDAY):
            response = self.client.get(self.url)
            self.assertFalse(response.context['schedule'])
            self.assertNotContains(response, 'disabled>')
            self.client.post(self.create_url, {'slot_0_0': 'New week'})
        self.assertEqual(
            list(WeekSchedule.objects.order_by('week_start').values_list('week_start', flat=True)),
            [date(2026, 10, 11), date(2026, 10, 18)],
        )

    def test_empty_week_is_rejected_and_does_not_lock_the_button(self):
        with at(WEDNESDAY):
            response = self.client.post(self.create_url, {'slot_0_0': '   '}, follow=True)
        self.assertEqual(WeekSchedule.objects.count(), 0)
        self.assertContains(response, 'at least one hour')

    def test_overlong_text_is_rejected(self):
        with at(WEDNESDAY):
            response = self.client.post(self.create_url, {'slot_2_9': 'x' * 201}, follow=True)
        self.assertEqual(WeekSchedule.objects.count(), 0)
        self.assertContains(response, 'longer than 200')

    def test_failed_save_leaves_no_half_written_schedule(self):
        with at(WEDNESDAY), patch.object(ScheduleSlot.objects, 'bulk_create', side_effect=IntegrityError):
            response = self.client.post(self.create_url, {'slot_0_0': 'Sleep'}, follow=True)
        self.assertEqual(WeekSchedule.objects.count(), 0)
        self.assertContains(response, 'already created')

    def test_saving_requires_post(self):
        self.assertEqual(self.client.get(self.create_url).status_code, 405)

    def test_ignores_unknown_and_out_of_range_fields(self):
        with at(WEDNESDAY):
            self.client.post(self.create_url, {'slot_7_0': 'bad day', 'slot_0_24': 'bad hour', 'slot_1_1': 'ok'})
        self.assertEqual(list(ScheduleSlot.objects.values_list('text', flat=True)), ['ok'])

    def test_other_players_schedule_is_private(self):
        other = User.objects.create_user('rival', password='pw')
        mine_url = self.url
        with at(WEDNESDAY):
            self.client.logout()
            self.client.login(username='rival', password='pw')
            self.client.post(self.create_url, {'slot_0_0': 'Rival secret plan'})
            self.client.logout()
            self.client.login(username='player', password='pw')
            response = self.client.get(mine_url)
        self.assertFalse(response.context['schedule'])
        self.assertNotContains(response, 'Rival secret plan')
        self.assertEqual(WeekSchedule.objects.get().user, other)