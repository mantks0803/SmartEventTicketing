import os
import cloudinary
import cloudinary.uploader
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import Customer, Organizer, User, UserType
from authentication.permissions import IsActiveAccountPermission, IsAdminPermission
from events.models import EventStatusEnum
from orders.models import Order, OrderStatusEnum, Ticket
from .serializers import (
    CustomerRegisterSerializer, OrganizerRegisterSerializer, LoginSerializer,
    CustomerProfileSerializer, OrganizerProfileSerializer,
    AdminUserDetailSerializer, AdminUserListSerializer,
    AdminUserQuerySerializer, AdminUserSummarySerializer,
)

class CustomerRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerRegisterSerializer

class OrganizerRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrganizerRegisterSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            role = (
                'ADMIN'
                if user.is_superuser or user.is_staff
                else getattr(user, 'type', 'CUSTOMER')
            )
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'name': user.name,
                    'avatar': getattr(user, 'avatar', None),
                    'role': role
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsActiveAccountPermission]

    def get(self, request):
        user = request.user
        if getattr(user, 'type', None) == 'ORGANIZER' and hasattr(user, 'organizer'):
            serializer = OrganizerProfileSerializer(user.organizer)
        elif hasattr(user, 'customer'):
            serializer = CustomerProfileSerializer(user.customer)
        else:
            return Response({'error': 'Không tìm thấy hồ sơ người dùng.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        if getattr(user, 'type', None) == 'ORGANIZER' and hasattr(user, 'organizer'):
            serializer = OrganizerProfileSerializer(user.organizer, data=request.data, partial=True)
        elif hasattr(user, 'customer'):
            serializer = CustomerProfileSerializer(user.customer, data=request.data, partial=True)
        else:
            return Response({'error': 'Không tìm thấy hồ sơ người dùng.'}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated, IsActiveAccountPermission]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('avatar')
        if not file_obj:
            return Response({'error': 'Vui lòng chọn file hình ảnh.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in valid_extensions:
            return Response({'error': 'Định dạng file không hỗ trợ. Vui lòng chọn file JPG, PNG hoặc WEBP.'}, status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > 5 * 1024 * 1024:
            return Response({'error': 'Kích thước file vượt quá giới hạn 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upload_result = cloudinary.uploader.upload(file_obj, folder="tickethub_avatars")
            secure_url = upload_result.get('secure_url')
            request.user.avatar = secure_url
            request.user.save()
            return Response({'avatar': secure_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Lỗi upload hình ảnh lên Cloudinary: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsActiveAccountPermission]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')


        if not old_password or not new_password or not confirm_password:
            return Response({'error': 'Vui lòng điền đầy đủ thông tin mật khẩu.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(old_password):
            return Response({'error': 'Mật khẩu hiện tại không chính xác.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return Response({'error': 'Mật khẩu mới phải chứa ít nhất 6 ký tự.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Xác nhận mật khẩu mới không trùng khớp.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Cập nhật mật khẩu thành công.'}, status=status.HTTP_200_OK)


class AdminUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]
    pagination_class = AdminUserPagination

    def list(self, request, *args, **kwargs):
        # Báo lỗi rõ ràng khi filter hoặc tham số phân trang không hợp lệ.
        query_serializer = AdminUserQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        self.validated_filters = query_serializer.validated_data
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        filters = getattr(self, 'validated_filters', {})
        queryset = User.objects.all().order_by('-date_joined', '-id')

        search = filters.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )

        role = filters.get('role')
        if role == UserType.ADMIN:
            queryset = queryset.filter(
                Q(type=UserType.ADMIN)
                | Q(is_staff=True)
                | Q(is_superuser=True)
            )
        elif role in [UserType.CUSTOMER, UserType.ORGANIZER]:
            # Staff/superuser được xem là Admin dù field type có giá trị khác.
            queryset = queryset.filter(
                type=role,
                is_staff=False,
                is_superuser=False,
            )

        account_status = filters.get('account_status')
        if account_status == 'ACTIVE':
            queryset = queryset.filter(status=True, is_active=True)
        elif account_status == 'LOCKED':
            queryset = queryset.filter(
                Q(status=False) | Q(is_active=False)
            )

        return queryset


class AdminUserSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]

    def get(self, request):
        non_admin = Q(is_staff=False, is_superuser=False)
        summary = User.objects.aggregate(
            total_users=Count('id'),
            total_customers=Count(
                'id',
                filter=Q(type=UserType.CUSTOMER) & non_admin,
            ),
            total_organizers=Count(
                'id',
                filter=Q(type=UserType.ORGANIZER) & non_admin,
            ),
            total_admins=Count(
                'id',
                filter=(
                    Q(type=UserType.ADMIN)
                    | Q(is_staff=True)
                    | Q(is_superuser=True)
                ),
            ),
            total_locked=Count(
                'id',
                filter=Q(status=False) | Q(is_active=False),
            ),
        )

        serializer = AdminUserSummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)


def get_admin_user_statistics(user):
    """Tính thống kê theo vai trò bằng các query riêng để không nhân dữ liệu."""
    if user.is_staff or user.is_superuser or user.type == UserType.ADMIN:
        return {}

    if user.type == UserType.CUSTOMER:
        try:
            customer = user.customer
        except Customer.DoesNotExist:
            return {
                'total_orders': 0,
                'paid_orders': 0,
                'total_tickets': 0,
                'total_paid_amount': Decimal('0.00'),
            }

        order_result = Order.objects.filter(customer=customer).aggregate(
            total_orders=Count('id'),
            paid_orders=Count(
                'id',
                filter=Q(status=OrderStatusEnum.PAID),
            ),
            total_paid_amount=Sum(
                'total_amount',
                filter=Q(status=OrderStatusEnum.PAID),
            ),
        )
        total_tickets = Ticket.objects.filter(
            order__customer=customer,
            order__status=OrderStatusEnum.PAID,
        ).count()

        return {
            'total_orders': order_result['total_orders'],
            'paid_orders': order_result['paid_orders'],
            'total_tickets': total_tickets,
            'total_paid_amount': (
                order_result['total_paid_amount'] or Decimal('0.00')
            ),
        }

    if user.type == UserType.ORGANIZER:
        try:
            organizer = user.organizer
        except Organizer.DoesNotExist:
            return {
                'total_events': 0,
                'pending_events': 0,
                'published_events': 0,
                'cancelled_events': 0,
                'total_revenue': Decimal('0.00'),
            }

        event_result = organizer.events.aggregate(
            total_events=Count('id'),
            pending_events=Count(
                'id',
                filter=Q(status=EventStatusEnum.PENDING),
            ),
            published_events=Count(
                'id',
                filter=Q(status=EventStatusEnum.PUBLISHED),
            ),
            cancelled_events=Count(
                'id',
                filter=Q(status=EventStatusEnum.CANCELLED),
            ),
        )
        total_revenue = Order.objects.filter(
            event__organizer=organizer,
            status=OrderStatusEnum.PAID,
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        return {**event_result, 'total_revenue': total_revenue}

    return {}


class AdminUserDetailView(generics.RetrieveAPIView):
    serializer_class = AdminUserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        return User.objects.select_related('customer', 'organizer')

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        context = self.get_serializer_context()
        context['statistics'] = get_admin_user_statistics(user)
        serializer = self.get_serializer(user, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserAccountStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]
    lock_account = None

    def post(self, request, user_id):
        with transaction.atomic():
            target_user = get_object_or_404(
                User.objects.select_for_update(),
                id=user_id,
            )

            if self.lock_account:
                if target_user.id == request.user.id:
                    return Response(
                        {
                            'error': 'Bạn không thể khóa tài khoản đang đăng nhập.',
                            'code': 'cannot_lock_self',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if (
                    target_user.type == UserType.ADMIN
                    or target_user.is_staff
                    or target_user.is_superuser
                ):
                    return Response(
                        {
                            'error': 'Không thể thay đổi trạng thái tài khoản Admin.',
                            'code': 'cannot_change_admin_status',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not target_user.status and not target_user.is_active:
                    return Response(
                        {
                            'error': 'Tài khoản đã bị khóa trước đó.',
                            'code': 'account_already_locked',
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                target_user.status = False
                target_user.is_active = False
                message = 'Khóa tài khoản thành công.'
            else:
                if (
                    target_user.type == UserType.ADMIN
                    or target_user.is_staff
                    or target_user.is_superuser
                ):
                    return Response(
                        {
                            'error': 'Không thể thay đổi trạng thái tài khoản Admin.',
                            'code': 'cannot_change_admin_status',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if target_user.status and target_user.is_active:
                    return Response(
                        {
                            'error': 'Tài khoản đang hoạt động.',
                            'code': 'account_already_active',
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                target_user.status = True
                target_user.is_active = True
                message = 'Mở khóa tài khoản thành công.'

            target_user.save(update_fields=['status', 'is_active'])

        serializer = AdminUserListSerializer(
            target_user,
            context={'request': request},
        )
        return Response(
            {'message': message, 'user': serializer.data},
            status=status.HTTP_200_OK,
        )
