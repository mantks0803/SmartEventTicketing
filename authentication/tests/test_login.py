from rest_framework.test import APITestCase

from authentication.models import Customer, User


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer-login',
            email='customer-login@example.com',
            phone_number='0901000010',
            name='Customer Login',
            type='CUSTOMER',
            password='123456',
        )
        Customer.objects.create(user=self.user)

    def test_customer_can_login_with_email(self):
        # Act: đăng nhập bằng email và mật khẩu đúng.
        response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': '123456',
            },
            format='json',
        )

        # Assert: API cấp hai token và trả đúng vai trò.
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], 'CUSTOMER')

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': 'wrong-password',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access', response.data)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.user.email,
                'password': '123456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access', response.data)

    def test_superuser_login_returns_admin_role(self):
        admin = User.objects.create_superuser(
            username='super-admin',
            email='super-admin@example.com',
            phone_number='0901000011',
            name='Super Admin',
            password='123456',
        )

        response = self.client.post(
            '/api/auth/login/',
            {
                'email': admin.email,
                'password': '123456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['role'], 'ADMIN')
