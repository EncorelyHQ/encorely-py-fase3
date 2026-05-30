"""
API tests for User authentication and registration.
Verifies the integration between DRF views and the Service layer.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserAuth:
    
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_registration_creates_vector(self, client):
        """Verifica que el registro cree el usuario y su MusicVibeVector"""
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'new@user.com',
            'password': 'EncorelyPass123!',
            'password_confirm': 'EncorelyPass123!',
            'display_name': 'New User',
            'concert_mood': 'moshpit',
            'city': 'Bogotá'
        }
        response = client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"DEBUG: Registration failed with {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(username='newuser')
        assert hasattr(user, 'vibe_vector')
        assert user.display_name == 'New User'

    def test_login_returns_jwt(self, client):
        """Verifica que el login retorne los tokens y la info del usuario"""
        user = User.objects.create_user(username='loginuser', password='password123')
        url = '/api/auth/login/'
        data = {'username': 'loginuser', 'password': 'password123'}
        
        response = client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'loginuser'
