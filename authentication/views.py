from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomerRegisterSerializer, OrganizerRegisterSerializer, LoginSerializer

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
                    'role': getattr(user, 'type', 'CUSTOMER')
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)