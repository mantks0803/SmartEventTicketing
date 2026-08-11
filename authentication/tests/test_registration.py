from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User


class RegistrationTests(APITestCase):
    def test_customer_can_register(self):
        # Arrange: chuẩn bị thông tin đăng ký hợp lệ.
        payload = {
            'name': 'Nguyen Van A',
            'username': 'customer-a',
            'email': 'customer-a@example.com',
            'phone_number': '0901000001',
            'dob': '2002-05-10',
            'password': '123456',
        }

        # Act: gọi API đăng ký khách hàng.
        response = self.client.post(
            '/api/auth/register/customer/',
            payload,
            format='json',
        )

        # Assert: User và hồ sơ Customer được tạo, mật khẩu đã được mã hóa.
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=payload['email'])
        self.assertEqual(user.type, 'CUSTOMER')
        self.assertTrue(user.check_password(payload['password']))
        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_organizer_can_register(self):
        payload = {
            'name': 'Organizer A',
            'username': 'organizer-a',
            'email': 'organizer-a@example.com',
            'phone_number': '0901000002',
            'company_name': 'Cong ty Su kien A',
            'bank_account': '123456789',
            'password': '123456',
        }

        response = self.client.post(
            '/api/auth/register/organizer/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=payload['email'])
        organizer = Organizer.objects.get(user=user)
        self.assertEqual(user.type, 'ORGANIZER')
        self.assertEqual(organizer.company_name, payload['company_name'])
        self.assertEqual(organizer.bank_account, payload['bank_account'])

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username='existing-user',
            email='existing@example.com',
            phone_number='0901000003',
            name='Existing User',
            password='123456',
        )
        payload = {
            'name': 'Duplicate User',
            'username': 'new-username',
            'email': 'existing@example.com',
            'phone_number': '0901000004',
            'password': '123456',
        }

        response = self.client.post(
            '/api/auth/register/customer/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)
