from django.db import models
from django.contrib.auth.models import AbstractUser

class UserType(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    CUSTOMER = 'CUSTOMER', 'Customer'
    ORGANIZER = 'ORGANIZER', 'Organizer'

class CustomerTierEnum(models.TextChoices):
    MEMBER = 'MEMBER', 'Member'
    SILVER = 'SILVER', 'Silver'
    GOLD = 'GOLD', 'Gold'
    PLATINUM = 'PLATINUM', 'Platinum'

class User(AbstractUser):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.CUSTOMER)
    status = models.BooleanField(default=True)
    avatar = models.CharField(max_length=500, default='https://default-avatar.com/user.png')
    dob = models.DateField(null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'name', 'phone_number']

    def __str__(self):
        return f"{self.username} ({self.type})"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='customer')
    tier = models.CharField(max_length=20, choices=CustomerTierEnum.choices, default=CustomerTierEnum.MEMBER)

    def __str__(self):
        return f"Customer: {self.user.name}"

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='organizer')
    company_name = models.CharField(max_length=250)
    bank_account = models.CharField(max_length=100)

    def __str__(self):
        return f"Organizer: {self.company_name}"