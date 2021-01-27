from datetime import datetime

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .models import User, Organization


FAKE_ORGS = {
    'AAAIMX': {
        'name': 'AAAIMX',
        'phone': '9999999',
        'address': 'MID, MX'
    }
}

FAKE_USERS = {
    'ADMIN': {
        'email': 'admin@test.org',
        'name': 'Raul Novelo',
        'password': '12345',
        'birthdate': datetime.now()
    },
    'VIEWER': {
        'email': 'viewer@test.org',
        'name': 'Viewer User Example',
        'password': '12345',
        'birthdate': datetime.now()
    },
    'USER': {
        'email': 'johndoe@test.org',
        'name': 'John Doe',
        'password': '12345',
        'birthdate': datetime.now()
    }
}

UNAUTHORIZED_MESSAGE = {
    'detail': 'Authentication credentials were not provided.'
}


class APITests(APITestCase):

    def setUp(self):
        # get groups
        admin_group = Group.objects.get(name='Administrator')
        viewer_group = Group.objects.get(name='Viewer')

        # create fake orgs
        aaaimx = Organization.objects.create(**FAKE_ORGS['AAAIMX'])

        # create fake users
        admin_user = User.objects.create_user(**FAKE_USERS['ADMIN'])
        admin_user.groups.add(admin_group)
        admin_user.organization = aaaimx
        admin_user.save()

        viewer_user = User.objects.create_user(**FAKE_USERS['VIEWER'])
        viewer_user.groups.add(viewer_group)
        viewer_user.organization = aaaimx
        viewer_user.save()

    def test_auth_login(self):

        # no active account
        data = {'email': 'test@test.org', 'password': '12345'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # wrong password
        data = {'email': 'admin@test.org', 'password': 'wrong password'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # success login
        data = {'email': 'admin@test.org', 'password': '12345'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_groups(self):

        # no token provided
        response = self.client.get('/api/auth/groups/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), UNAUTHORIZED_MESSAGE)

        # get access token
        data = {'email': 'admin@test.org', 'password': '12345'}
        response = self.client.post('/api/auth/login/', data, format='json')
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # sucess access to groups
        response = self.client.get('/api/auth/groups/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 2)

    def test_users(self):
        pass
    
    def test_orgs(self):
        pass