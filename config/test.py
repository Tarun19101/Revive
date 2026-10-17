import re
from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

MOMENT = datetime(2026, 10, 16, 16, 28)
EXPECTED = '16-10-2026 ::: Friday ::: 04:28 pm'


def tab_title(html):
    return re.search(r'<title>(.*?)</title>', html, re.S).group(1)


class TitleClockTests(TestCase):
    """Every sidebar page shows the clock in the tab title and in the page, in the same format."""

    PAGES = ['dashboard', 'profile', 'progress', 'schedule',
             'habit_list', 'quest_list', 'deepwork_home', 'bank_home']

    def setUp(self):
        User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')

    def test_each_sidebar_page_shows_the_clock_in_the_tab_and_in_the_page(self):
        for name in self.PAGES:
            with self.subTest(page=name), patch('config.context_processors.now', return_value=MOMENT):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertEqual(tab_title(html), EXPECTED)
                self.assertIn(f'>{EXPECTED}</p>', html)

    def test_pages_outside_the_sidebar_keep_their_own_titles(self):
        self.client.logout()
        self.assertEqual(tab_title(self.client.get(reverse('login')).content.decode()), 'Login')
        self.assertEqual(tab_title(self.client.get(reverse('register')).content.decode()), 'Register')