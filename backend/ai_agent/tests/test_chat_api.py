from decimal import Decimal
from unittest.mock import patch

from rest_framework.test import APITestCase

from ai_agent.models import (
    ChatMessage,
    ChatSenderEnum,
    ChatSession,
)
from authentication.models import (
    Customer,
    Organizer,
    User,
    UserType,
)


class ChatApiTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='chat-customer',
            email='chat-customer@example.com',
            phone_number='0912000001',
            name='Chat Customer',
            type=UserType.CUSTOMER,
            password='123456',
        )
        Customer.objects.create(user=self.customer_user)

        self.other_customer_user = User.objects.create_user(
            username='other-chat-customer',
            email='other-chat-customer@example.com',
            phone_number='0912000002',
            name='Other Chat Customer',
            type=UserType.CUSTOMER,
            password='123456',
        )
        Customer.objects.create(user=self.other_customer_user)

        self.organizer_user = User.objects.create_user(
            username='chat-organizer',
            email='chat-organizer@example.com',
            phone_number='0912000003',
            name='Chat Organizer',
            type=UserType.ORGANIZER,
            password='123456',
        )
        Organizer.objects.create(
            user=self.organizer_user,
            company_name='Chat Organizer Company',
            bank_account='123456789',
        )

    @patch('ai_agent.views.answer_with_rag')
    def test_customer_can_chat_with_general_mode(
        self,
        mock_answer_with_rag,
    ):
        mock_answer_with_rag.return_value = {
            'answer': 'Hệ thống giữ ghế trong 10 phút.',
            'sources': [
                {
                    'title': 'Chọn ghế và giữ ghế',
                    'source_path': 'customer/02_seat_hold.md',
                }
            ],
        }
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Tôi được giữ ghế bao lâu?',
                'mode': 'GENERAL',
                'audience': 'ORGANIZER',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mode'], 'GENERAL')
        self.assertEqual(
            response.data['answer'],
            'Hệ thống giữ ghế trong 10 phút.',
        )
        self.assertEqual(len(response.data['sources']), 1)
        self.assertEqual(response.data['recommended_events'], [])
        self.assertIsNone(response.data['event_availability'])
        self.assertIsNone(response.data['cost_breakdown'])
        self.assertIsNone(
            response.data['ticket_price_suggestion']
        )

        session = ChatSession.objects.get(
            id=response.data['session_id']
        )
        self.assertEqual(session.user, self.customer_user)

        messages = list(
            session.messages.order_by('timestamp', 'id')
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(
            messages[0].sender,
            ChatSenderEnum.USER,
        )
        self.assertEqual(
            messages[1].sender,
            ChatSenderEnum.ASSISTANT,
        )

        call_kwargs = mock_answer_with_rag.call_args.kwargs
        self.assertEqual(call_kwargs['audience'], 'CUSTOMER')
        self.assertEqual(
            call_kwargs['question'],
            'Tôi được giữ ghế bao lâu?',
        )

    @patch('ai_agent.views.answer_with_rag')
    def test_organizer_uses_organizer_audience(
        self,
        mock_answer_with_rag,
    ):
        mock_answer_with_rag.return_value = {
            'answer': 'Ban tổ chức nên lập ngân sách trước.',
            'sources': [],
        }
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Tôi nên lập ngân sách thế nào?',
                'mode': 'GENERAL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            mock_answer_with_rag.call_args.kwargs['audience'],
            'ORGANIZER',
        )

    @patch('ai_agent.views.answer_with_rag')
    def test_chat_uses_last_eight_messages_as_memory(
        self,
        mock_answer_with_rag,
    ):
        session = ChatSession.objects.create(
            user=self.customer_user
        )

        for index in range(10):
            sender = (
                ChatSenderEnum.USER
                if index % 2 == 0
                else ChatSenderEnum.ASSISTANT
            )
            ChatMessage.objects.create(
                session=session,
                sender=sender,
                text=f'Message {index}',
            )

        mock_answer_with_rag.return_value = {
            'answer': 'Giá vé cần dựa trên chi phí.',
            'sources': [],
        }
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'session_id': session.id,
                'message': 'Còn giá vé thì sao?',
                'mode': 'GENERAL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        call_kwargs = mock_answer_with_rag.call_args.kwargs
        history = call_kwargs['conversation_history']
        retrieval_query = call_kwargs['retrieval_query']

        self.assertEqual(len(history), 8)
        self.assertEqual(history[0]['text'], 'Message 2')
        self.assertEqual(history[-1]['text'], 'Message 9')
        self.assertIn('Message 8', retrieval_query)
        self.assertIn('Còn giá vé thì sao?', retrieval_query)
        self.assertEqual(
            ChatMessage.objects.filter(session=session).count(),
            12,
        )

    @patch('ai_agent.views.answer_with_rag')
    def test_user_cannot_use_another_users_session(
        self,
        mock_answer_with_rag,
    ):
        other_session = ChatSession.objects.create(
            user=self.other_customer_user
        )
        self.client.force_authenticate(self.customer_user)

        chat_response = self.client.post(
            '/api/ai/chat/',
            {
                'session_id': other_session.id,
                'message': 'Đây là session của ai?',
                'mode': 'GENERAL',
            },
            format='json',
        )
        history_response = self.client.get(
            f'/api/ai/sessions/{other_session.id}/messages/'
        )

        self.assertEqual(chat_response.status_code, 404)
        self.assertEqual(history_response.status_code, 404)
        self.assertEqual(other_session.messages.count(), 0)
        mock_answer_with_rag.assert_not_called()

    @patch('ai_agent.views.recommend_events')
    def test_recommend_event_returns_database_results(
        self,
        mock_recommend_events,
    ):
        mock_recommend_events.return_value = [
            {
                'event_id': 10,
                'title': 'Concert mùa hè',
                'thumbnail': 'https://example.com/concert.jpg',
                'location': 'TP.HCM',
                'start_time': '2026-09-10T19:00:00+07:00',
                'category': 'MUSIC',
                'min_ticket_price': Decimal('200000.00'),
                'max_ticket_price': Decimal('500000.00'),
                'available_seats': 40,
            }
        ]
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Tìm sự kiện âm nhạc ở TP.HCM',
                'mode': 'RECOMMEND_EVENT',
                'preferences': {
                    'category': 'MUSIC',
                    'location': 'TP.HCM',
                    'max_price': '500000',
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['recommended_events'][0]['event_id'],
            10,
        )
        self.assertEqual(response.data['sources'], [])
        self.assertIsNone(response.data['cost_breakdown'])

        call_kwargs = mock_recommend_events.call_args.kwargs
        self.assertEqual(call_kwargs['category'], 'MUSIC')
        self.assertEqual(call_kwargs['location'], 'TP.HCM')
        self.assertEqual(
            call_kwargs['max_price'],
            Decimal('500000.00'),
        )

    @patch('ai_agent.views.check_event_availability')
    def test_recommend_mode_checks_availability(
        self,
        mock_check_event_availability,
    ):
        mock_check_event_availability.return_value = {
            'status': 'found',
            'message': 'Đã tìm thấy thông tin ghế.',
            'event_id': 12,
            'title': 'Đêm nhạc mùa hè',
            'available_seats': 15,
            'total_seats': 30,
            'ticket_types': [],
        }
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Sự kiện này còn ghế không?',
                'mode': 'RECOMMEND_EVENT',
                'preferences': {
                    'event_id': 12,
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['event_availability']['event_id'],
            12,
        )
        self.assertEqual(response.data['recommended_events'], [])
        mock_check_event_availability.assert_called_once_with(
            event_id=12,
            event_name=None,
        )

    @patch('ai_agent.views.answer_with_rag')
    @patch('ai_agent.views.suggest_ticket_price')
    @patch('ai_agent.views.estimate_event_budget')
    def test_plan_event_returns_budget_and_ticket_price(
        self,
        mock_estimate_event_budget,
        mock_suggest_ticket_price,
        mock_answer_with_rag,
    ):
        budget = {
            'guest_count': 500,
            'quality_level': 'STANDARD',
            'location': 'TP.HCM',
            'min_cost': Decimal('80000000.00'),
            'max_cost': Decimal('100000000.00'),
            'contingency_rate': Decimal('0.10'),
            'contingency': Decimal('10000000.00'),
            'total_estimated_cost': Decimal('110000000.00'),
            'breakdown': [],
        }
        ticket_price = {
            'total_estimated_cost': Decimal('110000000.00'),
            'expected_ticket_sales': 500,
            'category': 'MUSIC',
            'breakeven_price': Decimal('220000.00'),
            'market_reference_avg_price': Decimal('300000.00'),
        }

        mock_estimate_event_budget.return_value = budget
        mock_suggest_ticket_price.return_value = ticket_price
        mock_answer_with_rag.return_value = {
            'answer': 'Chi phí dự kiến khoảng 110 triệu đồng.',
            'sources': [
                {
                    'title': 'Lập ngân sách sự kiện',
                    'source_path': 'organizer/02_budget_planning.md',
                }
            ],
        }
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Lập kế hoạch concert 500 người',
                'mode': 'PLAN_EVENT',
                'preferences': {
                    'guest_count': 500,
                    'quality_level': 'STANDARD',
                    'location': 'TP.HCM',
                    'service_categories': [
                        'VENUE',
                        'SOUND_LIGHT',
                    ],
                    'duration_hours': '4',
                    'category': 'MUSIC',
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['cost_breakdown']['guest_count'],
            500,
        )
        self.assertEqual(
            response.data['ticket_price_suggestion']['category'],
            'MUSIC',
        )
        self.assertEqual(response.data['recommended_events'], [])

        estimate_kwargs = (
            mock_estimate_event_budget.call_args.kwargs
        )
        self.assertEqual(estimate_kwargs['guest_count'], 500)
        self.assertEqual(
            estimate_kwargs['quality_level'],
            'STANDARD',
        )

        ticket_kwargs = mock_suggest_ticket_price.call_args.kwargs
        self.assertEqual(
            ticket_kwargs['total_estimated_cost'],
            Decimal('110000000.00'),
        )
        self.assertEqual(ticket_kwargs['guest_count'], 500)
        self.assertEqual(ticket_kwargs['category'], 'MUSIC')

        rag_kwargs = mock_answer_with_rag.call_args.kwargs
        self.assertEqual(
            rag_kwargs['structured_data']['budget'],
            budget,
        )
        self.assertEqual(
            rag_kwargs['structured_data']['ticket_price'],
            ticket_price,
        )

    def test_invalid_request_does_not_create_session(self):
        self.client.force_authenticate(self.organizer_user)

        invalid_mode_response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Test',
                'mode': 'INVALID_MODE',
            },
            format='json',
        )
        missing_plan_response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Tư vấn tổ chức sự kiện',
                'mode': 'PLAN_EVENT',
                'preferences': {
                    'guest_count': 100,
                },
            },
            format='json',
        )
        long_message_response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'a' * 1001,
                'mode': 'GENERAL',
            },
            format='json',
        )

        self.assertEqual(invalid_mode_response.status_code, 400)
        self.assertEqual(missing_plan_response.status_code, 400)
        self.assertEqual(long_message_response.status_code, 400)
        self.assertEqual(ChatSession.objects.count(), 0)
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_history_only_returns_own_data(self):
        first_session = ChatSession.objects.create(
            user=self.customer_user
        )
        second_session = ChatSession.objects.create(
            user=self.customer_user
        )
        ChatSession.objects.create(
            user=self.other_customer_user
        )

        ChatMessage.objects.create(
            session=second_session,
            sender=ChatSenderEnum.USER,
            text='Câu hỏi của tôi',
        )
        ChatMessage.objects.create(
            session=second_session,
            sender=ChatSenderEnum.ASSISTANT,
            text='Câu trả lời của trợ lý',
        )

        self.client.force_authenticate(self.customer_user)

        sessions_response = self.client.get('/api/ai/sessions/')
        messages_response = self.client.get(
            f'/api/ai/sessions/{second_session.id}/messages/'
        )

        self.assertEqual(sessions_response.status_code, 200)
        self.assertEqual(len(sessions_response.data), 2)
        self.assertEqual(
            sessions_response.data[0]['id'],
            second_session.id,
        )
        self.assertEqual(
            sessions_response.data[1]['id'],
            first_session.id,
        )
        self.assertEqual(messages_response.status_code, 200)
        self.assertEqual(len(messages_response.data), 2)
        self.assertEqual(
            messages_response.data[0]['sender'],
            ChatSenderEnum.USER,
        )
        self.assertEqual(
            messages_response.data[1]['sender'],
            ChatSenderEnum.ASSISTANT,
        )

    def test_authentication_and_active_account_are_required(self):
        anonymous_response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Xin chào',
                'mode': 'GENERAL',
            },
            format='json',
        )

        self.customer_user.status = False
        self.customer_user.save(update_fields=['status'])
        self.client.force_authenticate(self.customer_user)

        locked_response = self.client.post(
            '/api/ai/chat/',
            {
                'message': 'Xin chào',
                'mode': 'GENERAL',
            },
            format='json',
        )

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(locked_response.status_code, 403)
