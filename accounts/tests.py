from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountsTests(TestCase):
	def test_registration_logs_user_in(self):
		response = self.client.post(
			'/accounts/register/',
			{
				'username': 'newuser',
				'password1': 'A-secure-password-123',
				'password2': 'A-secure-password-123',
			},
		)

		self.assertRedirects(response, '/accounts/profile/')
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertTrue(get_user_model().objects.filter(username='newuser').exists())

	def test_login_and_logout(self):
		user = get_user_model().objects.create_user(
			username='existing',
			password='A-secure-password-123',
		)

		response = self.client.post(
			'/accounts/login/',
			{'username': user.username, 'password': 'A-secure-password-123'},
		)
		self.assertRedirects(response, '/accounts/profile/')

		response = self.client.post('/accounts/logout/')
		self.assertRedirects(response, '/accounts/login/')

	def test_profile_requires_login(self):
		response = self.client.get('/accounts/profile/')

		self.assertRedirects(
			response,
			'/accounts/login/?next=/accounts/profile/',
		)

	def test_login_rejects_external_next_url(self):
		user = get_user_model().objects.create_user(
			username='existing',
			password='A-secure-password-123',
		)

		response = self.client.post(
			'/accounts/login/',
			{
				'username': user.username,
				'password': 'A-secure-password-123',
				'next': 'https://example.com',
			},
		)

		self.assertRedirects(response, '/accounts/profile/')
