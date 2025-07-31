from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from authorization.models import UserCreds

class AuthorizationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('authorization:signup')
        self.signup_post_url = reverse('authorization:getUserData')
        self.login_url = reverse('authorization:login')
        self.login_post_url = reverse('authorization:loginCheck')
        self.logout_url = reverse('authorization:logout')
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@example.com')
        self.user_creds = UserCreds.objects.create(username='testuser', email='test@example.com')

    def test_signup_page_loads(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authorization/signup.html')

    def test_successful_signup(self):
        response = self.client.post(self.signup_post_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        })
        # Should show OTP page (show_otp in context)
        self.assertEqual(response.status_code, 200)
        self.assertIn('show_otp', response.context)
        self.assertTrue(response.context['show_otp'])

    def test_signup_password_mismatch(self):
        response = self.client.post(self.signup_post_url, {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'pass1',
            'password_confirm': 'pass2'
        })
        self.assertContains(response, "Password do not match!", status_code=200)

    def test_signup_duplicate_username(self):
        response = self.client.post(self.signup_post_url, {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'pass',
            'password_confirm': 'pass'
        })
        self.assertContains(response, "User already exist with same credentials", status_code=200)

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authorization/login.html')

    def test_login_success(self):
        response = self.client.post(self.login_post_url, {
            'username': 'testuser',
            'password': 'testpass'
        }, follow=True)
        # Should redirect to stockslist:index
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_failure(self):
        response = self.client.post(self.login_post_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        }, follow=True)
        # Should redirect back to login with error message in session
        self.assertEqual(response.status_code, 200)
        self.assertIn('error_message', response.context or {})

    def test_logout(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.logout_url, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_protected_view_redirects(self):
        protected_url = reverse('stockslist:dashboard')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_model_str(self):
        self.assertEqual(str(self.user), 'testuser')
