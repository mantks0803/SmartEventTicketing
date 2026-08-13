from django.urls import path
from .views import (
    CustomerRegisterView, OrganizerRegisterView, LoginView,
    UserProfileView, AvatarUploadView, ChangePasswordView,
    AdminUserAccountStatusView, AdminUserDetailView, AdminUserListView,
    AdminUserSummaryView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/customer/', CustomerRegisterView.as_view(), name='register_customer'),
    path('register/organizer/', OrganizerRegisterView.as_view(), name='register_organizer'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path(
        'admin/users/summary/',
        AdminUserSummaryView.as_view(),
        name='admin_user_summary',
    ),
    path(
        'admin/users/<int:user_id>/',
        AdminUserDetailView.as_view(),
        name='admin_user_detail',
    ),
    path(
        'admin/users/<int:user_id>/lock/',
        AdminUserAccountStatusView.as_view(lock_account=True),
        name='admin_user_lock',
    ),
    path(
        'admin/users/<int:user_id>/unlock/',
        AdminUserAccountStatusView.as_view(lock_account=False),
        name='admin_user_unlock',
    ),
]
