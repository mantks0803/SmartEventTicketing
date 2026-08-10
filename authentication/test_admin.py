from rest_framework.test import APITestCase

from authentication.models import User


class AdminLoginTests(APITestCase):
    def test_superuser_login_returns_admin_role(self):
        User.objects.create_superuser(
            username='super-admin',
            email='super-admin@example.com',
            phone_number='0900000301',
            name='Super Admin',
            password='123456',
        )

        response = self.client.post(
            '/api/auth/login/',
            {
                'email': 'super-admin@example.com',
                'password': '123456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['role'], 'ADMIN')
