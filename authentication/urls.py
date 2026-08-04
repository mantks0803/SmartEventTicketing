from django.urls import path
from .views import CustomerRegisterView, OrganizerRegisterView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/customer/', CustomerRegisterView.as_view(), name='register_customer'),
    path('register/organizer/', OrganizerRegisterView.as_view(), name='register_organizer'),
]