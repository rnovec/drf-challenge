
from datetime import datetime
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .models import User, Organization
from .constants import (
    USER_INFO_FIELDS,
    USER_MODEL_FIELDS, ORG_INFO_FIELDS,
    UNAUTHORIZED_MESSAGE
)

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
        'email': 'guest@test.org',
        'name': 'John Doe',
        'password': '12345',
        'phone': '1357908642',
        'birthdate': datetime.now()
    }
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
        self.assertEqual(tuple(data['results'][0].keys()), USER_MODEL_FIELDS)

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
        self.client.login(email='guest@test.org', password='12345')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user(self):
        """
        Retrieve user information, and the organization id and name
        """
        guest = User.objects.get(email='guest@test.org')
        self.client.login(email='guest@test.org', password='12345')
        response = self.client.get('/api/users/%d/' % guest.id)
        data = response.json()

        # validate user and organization fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(list(data.keys())), sorted(USER_INFO_FIELDS))
        self.assertEqual(
            sorted(list(data['organization'].keys())), ['id', 'name'])

    def test_create_users(self):
        """
        Create an user for the organization, must set password as well.
        Request user must be Administrator
        """
        data = {
            'email': 'example@example.org',
            'name': 'Example User',
            'password': '54321'
        }
        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email='admin@test.org', password='12345')
        response = self.client.post('/api/users/', data, format='json')
        data = response.json()
        user_created = User.objects.get(pk=data['id'])
        user_admin = User.objects.get(email='admin@test.org')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user_created.organization, user_admin.organization)

    def test_update_users(self):
        """
        Update user information for the user_id if request user is
        `Administrator` of his organization. Or request user is user_id
        """
        admin = User.objects.get(email='admin@test.org')
        viewer = User.objects.get(email='viewer@test.org')
        guest = User.objects.get(email='guest@test.org')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.patch(
            '/api/users/%d/' % admin.id, {'email': 'example1@aaaimx.org'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # account owner
        response = self.client.patch(
            '/api/users/%d/' % guest.id, {'email': 'example2@aaaimx.org'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # administrator of the org
        self.client.login(email='admin@test.org', password='12345')
        response = self.client.patch(
            '/api/users/%d/' % viewer.id, {'phone': '12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_users(self):
        """
        Delete user for the user_id if request user is `Administrator` of his organization
        """
        admin = User.objects.get(email='admin@test.org')
        viewer = User.objects.get(email='viewer@test.org')
        guest = User.objects.get(email='guest@test.org')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.delete('/api/users/%d/' % admin.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # viewer role
        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.delete('/api/users/%d/' % admin.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # administrator of the org
        self.client.login(email='admin@test.org', password='12345')
        response = self.client.delete('/api/users/%d/' % viewer.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_retrieve_org(self):
        """
        Retrieve organization information if request user is `Administrator` or `Viewer`
        """
        aaaimx = Organization.objects.get(name='AAAIMX')
        lht = Organization.objects.get(name='Lighthouse Tech')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get('/api/organizations/%d/' % lht.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email='admin@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(list(response.json().keys())),
                         sorted(ORG_INFO_FIELDS))

        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_org_users(self):
        """
        List all the users for the user organization if user is
        `Administrator` or `Viewer`. Must return just id and name of the user
        """
        aaaimx = Organization.objects.get(name='AAAIMX')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/users/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email='admin@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/users/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 2)

        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.get('/api/organizations/%d/users/' % aaaimx.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_org_user_by_id(self):
        """
        Retrieve user id and name if if user is `Administrator` or `Viewer`
        """
        aaaimx = Organization.objects.get(name='AAAIMX')
        admin = User.objects.get(email='admin@test.org')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.get(
            '/api/organizations/%d/users/%d/' % (aaaimx.id, admin.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email='admin@test.org', password='12345')
        response = self.client.get(
            '/api/organizations/%d/users/%d/' % (aaaimx.id, admin.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(list(response.json().keys())), ['id', 'name'])

        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.get(
            '/api/organizations/%d/users/%d/' % (aaaimx.id, admin.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_org(self):
        """
        Update organization if request user is `Administrator`
        """
        aaaimx = Organization.objects.get(name='AAAIMX')
        lht = Organization.objects.get(name='Lighthouse Tech')

        self.client.login(email='guest@test.org', password='12345')
        response = self.client.patch(
            '/api/organizations/%d/' % aaaimx.id, {'address': 'Palo Alto, USA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(email='viewer@test.org', password='12345')
        response = self.client.patch(
            '/api/organizations/%d/' % aaaimx.id, {'address': 'Palo Alto, USA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # administrator of the org
        self.client.login(email='admin@test.org', password='12345')
        response = self.client.patch(
            '/api/organizations/%d/' % aaaimx.id, {'address': 'Palo Alto, USA'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_info(self):
        """
        Should return {`user_name`, `id`, `organization_name`, `public_ip`}
        Public Ip must be the internet public IP of the server where code is running
        """
        # sucess access to groups
        response = self.client.get('/api/info/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), UNAUTHORIZED_MESSAGE)

        # get access token
        data = {'email': 'admin@test.org', 'password': '12345'}
        response = self.client.post('/api/auth/login/', data, format='json')
        token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

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
