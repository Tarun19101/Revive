from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='pw')
        self.client.login(username='player', password='pw')

    def test_add_task_goes_into_the_single_list(self):
        response = self.client.post(reverse('add_task'), {'title': 'Buy rice'})
        self.assertRedirects(response, reverse('schedule'))
        task = Task.objects.get()
        self.assertEqual((task.user, task.title, task.status), (self.user, 'Buy rice', Task.PENDING))

    def test_blank_title_is_rejected_with_a_message(self):
        response = self.client.post(reverse('add_task'), {'title': '   '}, follow=True)
        self.assertEqual(Task.objects.count(), 0)
        self.assertContains(response, 'Enter a task title.')

    def test_completing_a_task_gives_5_xp(self):
        task = Task.objects.create(user=self.user, title='Do the thing')
        self.client.post(reverse('complete_task', args=[task.id]))
        task.refresh_from_db()
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(task.status, Task.COMPLETED)
        self.assertEqual(profile.xp, 5)

    def test_completing_twice_pays_once(self):
        task = Task.objects.create(user=self.user, title='Do the thing')
        url = reverse('complete_task', args=[task.id])
        self.client.post(url)
        self.client.post(url)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp, 5)

    def test_xp_rolls_over_into_the_next_level(self):
        profile = self.user.profile
        profile.level, profile.xp = 1, 48          # level 1 needs 50
        profile.save()
        task = Task.objects.create(user=self.user, title='Almost there')
        self.client.post(reverse('complete_task', args=[task.id]))
        profile.refresh_from_db()
        self.assertEqual((profile.level, profile.xp), (2, 3))

    def test_exactly_hitting_the_threshold_levels_up(self):
        profile = self.user.profile
        profile.level, profile.xp = 1, 45
        profile.save()
        task = Task.objects.create(user=self.user, title='On the line')
        self.client.post(reverse('complete_task', args=[task.id]))
        profile.refresh_from_db()
        self.assertEqual((profile.level, profile.xp), (2, 0))

    def test_cannot_complete_someone_elses_task(self):
        other = User.objects.create_user('rival', password='pw')
        task = Task.objects.create(user=other, title='Not yours')
        response = self.client.post(reverse('complete_task', args=[task.id]))
        self.assertEqual(response.status_code, 404)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.PENDING)

    def test_get_requests_cannot_add_or_complete(self):
        task = Task.objects.create(user=self.user, title='Safe from links')
        self.assertEqual(self.client.get(reverse('add_task')).status_code, 405)
        self.assertEqual(self.client.get(reverse('complete_task', args=[task.id])).status_code, 405)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.PENDING)

    def test_page_lists_only_pending_tasks(self):
        Task.objects.create(user=self.user, title='Still to do')
        Task.objects.create(user=self.user, title='Already done', status=Task.COMPLETED)
        response = self.client.get(reverse('schedule'))
        self.assertContains(response, 'Still to do')
        self.assertNotContains(response, 'Already done')

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.post(reverse('add_task'), {'title': 'x'}).status_code, 302)
        self.assertEqual(Task.objects.count(), 0)