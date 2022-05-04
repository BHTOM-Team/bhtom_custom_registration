import copy
from smtplib import SMTPException
from unittest.mock import patch

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.shortcuts import reverse
from django.test import override_settings, TestCase


@override_settings(ROOT_URLCONF='bhtom_custom_registration.bhtom_registration.tests.urls.test_open_urls')
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
        """Test that a user can register using the open registration flow."""
        response = self.client.post(reverse('registration:register'), data=self.user_data)
        user = User.objects.get(username=self.user_data['username'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.id, auth.get_user(self.client).id)

    @override_settings(TOM_REGISTRATION={'REGISTRATION_AUTHENTICATION_BACKEND': ''})
    def test_user_register_login_failure(self):
        """
        Test that an error message is logged correctly when a newly-registered user has an automated login failure.
        """
        del settings.REGISTRATION_AUTHENTICATION_BACKEND
        with self.assertLogs('bhtom_custom_registration.bhtom_registration.registration_flows.open.views', level='ERROR') as logs:
            response = self.client.post(reverse('registration:register'), data=self.user_data)
            self.assertIn(
                'ERROR:bhtom_custom_registration.bhtom_registration.registration_flows.open.views:Unable to log in newly registered user: '
                'You have multiple authentication backends configured and therefore must provide the `backend` argument'
                ' or set the `backend` attribute on the user.', logs.output)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(auth.get_user(self.client).is_anonymous)


@override_settings(ROOT_URLCONF='bhtom_custom_registration.bhtom_registration.tests.urls.test_approval_required_urls',
                   AUTHENTICATION_BACKENDS=(
                       'django.contrib.auth.backends.AllowAllUsersModelBackend',
                       'guardian.backends.ObjectPermissionBackend',
                   ),
                   TOM_REGISTRATION={
                        'REGISTRATION_AUTHENTICATION_BACKEND': 'django.contrib.auth.backends.AllowAllUsersModelBackend',
                        'REGISTRATION_REDIRECT_PATTERN': 'home',
                        'SEND_APPROVAL_EMAILS': True
                   },
                   MANAGERS=[('David', 'dcollom@lco.global')])
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
        """
        Test that a user can register using the approval registration flow, that the user is inactive, and that the user
        sees the correct error message if they attempt to log in prior to approval.
        """
        response = self.client.post(reverse('registration:register'), data=self.user_data)
        messages = [(m.message, m.level) for m in get_messages(response.wsgi_request)]
        user = User.objects.get(username=self.user_data['username'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], 'Your request to register has been submitted to the administrators.')
        self.assertFalse(user.is_active)
        self.assertTrue(auth.get_user(self.client).is_anonymous)

        response = self.client.post(reverse('registration:login'),
                                    data={
                                        'username': self.user_data['username'],
                                        'password': self.user_data['password1']
                                    }, follow=True)
        self.assertTrue(auth.get_user(self.client).is_anonymous)
        self.assertContains(response, 'Your registration is currently pending administrator approval.')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f'Registration Request from {self.user_data["first_name"]} {self.user_data["last_name"]}',
                      mail.outbox[0].subject)

    @patch('bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views.mail_managers')
    def test_user_register_email_send_failure(self, mock_mail_managers):
        """Test that a registration email send failure logs the correct error message."""
        mock_mail_managers.side_effect = SMTPException('exception content')
        with self.assertLogs('bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views', level='ERROR') as logs:
            self.client.post(reverse('registration:register'), data=self.user_data)
            self.assertIn(
                'ERROR:bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views:'
                'Unable to send email: exception content',
                logs.output)

    def test_user_approve(self):
        """Test that a user can log in following approval in the approval registration flow."""
        self.client.post(reverse('registration:register'), data=self.user_data)
        user = User.objects.get(username=self.user_data['username'])
        self.assertFalse(user.is_active)

        self.client.force_login(self.superuser)
        self.client.post(reverse('registration:approve', kwargs={'pk': user.id}), data=self.user_data)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(len(mail.outbox), 2)  # There should be two--one for the registration, one for the approval
        self.assertIn('Your registration has been approved!', mail.outbox[1].subject)

    @patch('bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views.send_mail')
    def test_user_approve_email_send_failure(self, mock_send_mail):
        """Test that an approval email send failure logs the correct error message."""
        self.client.force_login(self.superuser)
        test_user_data = copy.copy(self.user_data)
        test_user_data['password'] = test_user_data.pop('password1')
        test_user_data.pop('password2')
        user = User.objects.create(**test_user_data, is_active=False)
        mock_send_mail.side_effect = SMTPException('exception content')

        with self.assertLogs('bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views', level='ERROR') as logs:
            self.client.post(reverse('registration:approve', kwargs={'pk': user.id}), data=test_user_data)
            self.assertIn(
                'ERROR:bhtom_custom_registration.bhtom_registration.registration_flows.approval_required.views:'
                'Unable to send email: exception content',
                logs.output)


@override_settings(ROOT_URLCONF='bhtom_custom_registration.bhtom_registration.tests.urls.test_open_urls',
                   MIDDLEWARE=[
                        'django.middleware.security.SecurityMiddleware',
                        'django.contrib.sessions.middleware.SessionMiddleware',
                        'django.middleware.common.CommonMiddleware',
                        'django.middleware.csrf.CsrfViewMiddleware',
                        'django.contrib.auth.middleware.AuthenticationMiddleware',
                        'django.contrib.messages.middleware.MessageMiddleware',
                        'django.middleware.clickjacking.XFrameOptionsMiddleware',
                        'bhtom_common.middleware.Raise403Middleware',
                        'bhtom_common.middleware.ExternalServiceMiddleware',
                        'bhtom_common.middleware.AuthStrategyMiddleware',
                        'bhtom_custom_registration.bhtom_registration.middleware.RedirectAuthenticatedUsersFromRegisterMiddleware'])
class TestMiddleware(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')

    def test_redirect_authenticated_user_to_profile(self):
        """Test that an authenticated user is redirected to their profile if they attempt to reach the register page."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('registration:register'), follow=True)
        self.assertContains(response, 'Update')

    def test_no_redirection_for_anonymous_user(self):
        """
        Test that an anonymous user can successfully access the register page with the
        RedirectAuthenticatedUsersFromRegisterMiddleware enabled.
        """
        response = self.client.get(reverse('registration:register'), follow=True)
        self.assertNotContains(response, 'Update')
        self.assertContains(response, 'Register')
