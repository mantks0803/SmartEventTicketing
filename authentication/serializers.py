from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer, Organizer

User = get_user_model()

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'phone_number', 'dob', 'password']
        extra_kwargs = {
            'dob': {'required': False, 'allow_null': True},
            'phone_number': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        if 'dob' in validated_data and not validated_data['dob']:
            validated_data['dob'] = None

        validated_data['type'] = 'CUSTOMER'
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        Customer.objects.get_or_create(user=user)
        return user


class OrganizerRegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(required=True, write_only=True)
    bank_account = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'phone_number', 'company_name', 'bank_account', 'password']

    def create(self, validated_data):
        company_name = validated_data.pop('company_name', '')
        bank_account = validated_data.pop('bank_account', '')
        password = validated_data.pop('password')

        validated_data['type'] = 'ORGANIZER'
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        Organizer.objects.update_or_create(
            user=user,
            defaults={
                'company_name': company_name,
                'bank_account': bank_account
            }
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=username_or_email).first()
        if not user:
            user = User.objects.filter(username=username_or_email).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError('Tài khoản đã bị khóa.')
            attrs['user'] = user
            return attrs

        raise serializers.ValidationError('Tên đăng nhập/Email hoặc mật khẩu không chính xác.')