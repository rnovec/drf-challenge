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
    },
    'LHT': {
        'name': 'Lighthouse Tech',
        'phone': '111111',
        'address': 'MID, MX'
    }
}

FAKE_USERS = {
    'ADMIN': {
        'email': 'admin@test.org',
        'name': 'Raul Novelo',
        'password': '12345',
        'phone': '123456789',
        'birthdate': datetime.now()
    },
    'VIEWER': {
        'email': 'viewer@test.org',
        'name': 'Viewer User Example',
        'password': '12345',
        'phone': '987654321',
        'birthdate': datetime.now()
    },
    'USER': {
        'email': 'johndoe@test.org',
        'name': 'John Doe',
        'password': '12345',
        'phone': '1357908642',
        'birthdate': datetime.now()
    }
}

USER_MODEL_FIELDS = ['id', 'organization', 'groups', 'password', 'last_login', 'is_superuser',
                     'email', 'name', 'birthdate', 'phone', 'date_joined', 'is_staff', 'is_active', 'user_permissions']

UNAUTHORIZED_MESSAGE = {
    'detail': 'Authentication credentials were not provided.'
}


class APITests(APITestCase):

    def setUp(self):
        # get groups
        admin_group = Group.objects.get(name='Administrator')
        viewer_group = Group.objects.get(name='Viewer')

        # create orgs
        aaaimx = Organization.objects.create(**FAKE_ORGS['AAAIMX'])
        lht = Organization.objects.create(**FAKE_ORGS['LHT'])

        # create admin user
        admin_user = User.objects.create_user(**FAKE_USERS['ADMIN'])
        admin_user.groups.add(admin_group)
        admin_user.organization = aaaimx
        admin_user.save()

        # create viewer user
        viewer_user = User.objects.create_user(**FAKE_USERS['VIEWER'])
        viewer_user.groups.add(viewer_group)
        viewer_user.organization = aaaimx
        viewer_user.save()

        # create normal user
        viewer_user = User.objects.create_user(**FAKE_USERS['USER'])
        viewer_user.organization = lht
        viewer_user.save()

    def test_auth_login(self):
        """
        API must support JWT authentication.
        POST /api/auth/login/ using email address
        """

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
        """
        Should return Authentication Groups. Application should have:
        - Administrator: Full access to CRUD Any User in his org and RU Organization
        - Viewer: List and Retrieve and User in his org.
        - User: CRU his own user
        """

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

    def test_list_users(self):
        """
        List all the users for the user organization 
        if user is `Administrator` or `Viewer`. Must return all the user model fields.
        Should support search by name, email. Should support filter by phone.
        """
        self.client.login(email='admin@test.org', password='12345')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(list(data['results'][0].keys()), USER_MODEL_FIELDS)

        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

        # Search and filters
        response = self.client.get('/api/users/?search=Raul&phone=123456789')
        self.assertEqual(response.json()['count'], 1)

        response = self.client.get('/api/users/?search=Novelo&email=viewer@')
        self.assertEqual(response.json()['count'], 1)

        # avoid access to users without permissions 
        self.client.login(email='johndoe@test.org', password='12345')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_orgs(self):
        pass

    def test_info(self):
        # sucess access to groups
        response = self.client.get('/api/info/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), UNAUTHORIZED_MESSAGE)

        # get access token
        data = {'email': 'admin@test.org', 'password': '12345'}
        response = self.client.post('/api/auth/login/', data, format='json')
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Should return {`user_name`, `id`, `organization_name`, `public_ip`}
        # Public Ip must be the internet public IP of the server where code is running
        response = self.client.get('/api/info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['user_name'], FAKE_USERS['ADMIN']['name'])
        self.assertEqual(
            response.json()['organization_name'], FAKE_ORGS['AAAIMX']['name'])
        self.assertEqual(response.json()['public_ip'], 'testserver')

        # login with viewer account
        self.client.login(email='viewer@test.org', password='12345')

        response = self.client.get('/api/info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['user_name'], FAKE_USERS['VIEWER']['name'])
        self.assertEqual(
            response.json()['organization_name'], FAKE_ORGS['AAAIMX']['name'])
        self.assertEqual(response.json()['public_ip'], 'testserver')

