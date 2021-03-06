from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import override_settings, TestCase
from django.urls import get_resolver


@override_settings(ROOT_URLCONF='tom_registration.tests.urls.test_open_urls')
class TestOpenRegistrationViews(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'aaronrodgers',
            'first_name': 'Aaron',
            'last_name': 'Rodgers',
            'email': 'aaronrodgers@berkeley.edu',
            'password1': 'gopackgo',
            'password2': 'gopackgo',
        }

    def test_user_register(self):
        response = self.client.post(reverse('registration:register'), data=self.user_data)
        user = User.objects.get(username=self.user_data['username'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.id, auth.get_user(self.client).id)

    @override_settings(TOM_REGISTRATION={'REGISTRATION_AUTHENTICATION_BACKEND': ''})
    def test_user_register_login_failure(self):
        del settings.REGISTRATION_AUTHENTICATION_BACKEND
        with self.assertLogs('tom_registration.registration_flows.open.views', level='ERROR') as logs:
            response = self.client.post(reverse('registration:register'), data=self.user_data)
            self.assertIn(
                'ERROR:tom_registration.registration_flows.open.views:Unable to log in newly registered user: '
                'You have multiple authentication backends configured and therefore must provide the `backend` argument'
                ' or set the `backend` attribute on the user.', logs.output)
        user = User.objects.get(username=self.user_data['username'])

        self.assertEqual(response.status_code, 302)
        self.assertTrue(auth.get_user(self.client).is_anonymous)


@override_settings(ROOT_URLCONF='tom_registration.tests.urls.test_approval_required_urls',
                   AUTHENTICATION_BACKENDS=(
                       'django.contrib.auth.backends.AllowAllUsersModelBackend',
                       'guardian.backends.ObjectPermissionBackend',
                   ))
class TestApprovalRegistrationViews(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'aaronrodgers',
            'first_name': 'Aaron',
            'last_name': 'Rodgers',
            'email': 'aaronrodgers@berkeley.edu',
            'password1': 'gopackgo',
            'password2': 'gopackgo',
        }
        self.superuser = User.objects.create_superuser(username='superuser')

    def test_user_register(self):
        print(get_resolver().reverse_dict.keys())
        response = self.client.post(reverse('registration:register'), data=self.user_data)
        messages = [(m.message, m.level) for m in get_messages(response.wsgi_request)]
        user = User.objects.get(username=self.user_data['username'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], 'Your request to register has been submitted to the administrators.')
        self.assertFalse(user.is_active)
        self.assertTrue(auth.get_user(self.client).is_anonymous)

        print(messages)
        response = self.client.post(reverse('login'),
                                    data={
                                        'username': self.user_data['username'],
                                        'password': self.user_data['password1']
                                    }, follow=True)
        self.assertTrue(auth.get_user(self.client).is_anonymous)
        print(response.status_code)
        print(auth.get_user(self.client))
        messages = [(m.message, m.level) for m in get_messages(response.wsgi_request)]
        self.assertEqual(messages[0][0], '')  # TODO: Test that this message conveys the pending status
        print(messages)

    def test_user_approve(self):
        response = self.client.post(reverse('tom_registration:register'), data=self.user_data)
        user = User.objects.get(username=self.user_data['username'])
        self.assertFalse(user.is_active)

        # user_approval_data = copy(self.user_data)
        # user_approval_data.pop('password1')
        # user_approval_data.pop('password2')
        self.client.force_login(self.superuser)
        response = self.client.post(reverse('registration:approve', kwargs={'pk': user.id}), data=self.user_data)
        print(response.status_code)
        user.refresh_from_db()
        self.assertTrue(user.is_active)


class TestRegistrationExtras(TestCase):
    pass