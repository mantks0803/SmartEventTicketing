from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from events.models import User, Customer, Organizer, UserType, CustomerTierEnum



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    bank_account = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'phone_number', 'username', 
            'password', 'dob', 'type', 'company_name', 'bank_account'
        ]

    def validate_type(self, value):
        if value not in [UserType.CUSTOMER, UserType.ORGANIZER]:
            raise serializers.ValidationError("Loại tài khoản không hợp lệ khi tự đăng ký!")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        user_type = attrs.get('type')

        if user_type == UserType.ORGANIZER:
            errors = {}
            if not attrs.get('company_name'):
                errors['company_name'] = 'Tên công ty là bắt buộc cho người tổ chức.'
            if not attrs.get('bank_account'):
                errors['bank_account'] = 'Số tài khoản ngân hàng là bắt buộc cho người tổ chức.'

            if errors:
                raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        company_name = validated_data.pop('company_name', None)
        bank_account = validated_data.pop('bank_account', None)

        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)

        if user.type == UserType.CUSTOMER:
            Customer.objects.create(user=user, tier=CustomerTierEnum.MEMBER)
        elif user.type == UserType.ORGANIZER:
            Organizer.objects.create(
                user=user, 
                company_name=company_name, 
                bank_account=bank_account
            )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['type'] = str(user.type)
        return token