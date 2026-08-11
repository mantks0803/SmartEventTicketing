from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User


class EventThumbnailTests(APITestCase):
    def setUp(self):
        self.organizer_user = User.objects.create_user(
            username='thumbnail-organizer',
            email='thumbnail-organizer@example.com',
            phone_number='0902000021',
            name='Thumbnail Organizer',
            type='ORGANIZER',
            password='123456',
        )
        Organizer.objects.create(
            user=self.organizer_user,
            company_name='Thumbnail Company',
            bank_account='123456789',
        )
        self.customer_user = User.objects.create_user(
            username='thumbnail-customer',
            email='thumbnail-customer@example.com',
            phone_number='0902000022',
            name='Thumbnail Customer',
            type='CUSTOMER',
            password='123456',
        )
        Customer.objects.create(user=self.customer_user)

    @patch('events.views.cloudinary.uploader.upload')
    def test_organizer_can_upload_thumbnail(self, upload_mock):
        # Arrange: giả lập Cloudinary để test không tải ảnh thật lên mạng.
        upload_mock.return_value = {
            'secure_url': 'https://res.cloudinary.com/demo/event.jpg',
        }
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/events/upload-thumbnail/',
            {
                'thumbnail': SimpleUploadedFile(
                    'event.jpg',
                    b'fake-image-content',
                    content_type='image/jpeg',
                )
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['secure_url'],
            upload_mock.return_value['secure_url'],
        )
        upload_mock.assert_called_once()
        self.assertEqual(upload_mock.call_args.kwargs['folder'], 'smartticket_events')

    @patch('events.views.cloudinary.uploader.upload')
    def test_invalid_thumbnail_is_rejected_before_upload(self, upload_mock):
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/events/upload-thumbnail/',
            {
                'thumbnail': SimpleUploadedFile(
                    'event.txt',
                    b'not-an-image',
                    content_type='text/plain',
                )
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 400)
        upload_mock.assert_not_called()

    def test_customer_cannot_upload_thumbnail(self):
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/events/upload-thumbnail/',
            {
                'thumbnail': SimpleUploadedFile(
                    'event.jpg',
                    b'fake-image-content',
                    content_type='image/jpeg',
                )
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 403)
