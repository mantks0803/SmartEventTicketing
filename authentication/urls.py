from django.urls import path
from .views import (
    CustomerRegisterView, OrganizerRegisterView, LoginView,
    UserProfileView, AvatarUploadView, ChangePasswordView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/customer/', CustomerRegisterView.as_view(), name='register_customer'),
    path('register/organizer/', OrganizerRegisterView.as_view(), name='register_organizer'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]