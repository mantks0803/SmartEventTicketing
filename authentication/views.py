import os
import cloudinary
import cloudinary.uploader
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    CustomerRegisterSerializer, OrganizerRegisterSerializer, LoginSerializer,
    CustomerProfileSerializer, OrganizerProfileSerializer
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
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'name': user.name,
                    'avatar': getattr(user, 'avatar', None),
                    'role': getattr(user, 'type', 'CUSTOMER')
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

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