from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.get_or_create(user=self.user)
    
    def test_register_view(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_view(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_profile_requires_login(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
    
    def test_profile_accessible_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
