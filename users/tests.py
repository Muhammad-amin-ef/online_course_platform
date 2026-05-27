import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='test1234',
        is_instructor=False
    )


@pytest.fixture
def instructor(db):
    return User.objects.create_user(
        username='instructor',
        email='instructor@test.com',
        password='test1234',
        is_instructor=True
    )


@pytest.fixture
def auth_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def instructor_client(client, instructor):
    client.force_authenticate(user=instructor)
    return client


@pytest.mark.django_db
def test_register(client):
    url = reverse('register')
    data = {
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'newpass123',
        'is_instructor': False
    }
    response = client.post(url, data)
    assert response.status_code == 201


@pytest.mark.django_db
def test_login(client, user):
    url = reverse('token_obtain_pair')
    data = {'username': 'testuser', 'password': 'test1234'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_my_account(auth_client):
    url = reverse('my-account')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert response.data['username'] == 'testuser'