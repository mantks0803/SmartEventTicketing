from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Customer, Organizer, UserType

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
            if not user.is_active or not user.status:
                raise serializers.ValidationError('Tài khoản đã bị khóa.')
            attrs['user'] = user
            return attrs

        raise serializers.ValidationError('Tên đăng nhập/Email hoặc mật khẩu không chính xác.')


class CustomerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    name = serializers.CharField(source='user.name')
    phone_number = serializers.CharField(source='user.phone_number', required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)
    dob = serializers.DateField(source='user.dob', required=False, allow_null=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'username', 'phone_number', 'avatar', 'type', 'dob']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OrganizerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    name = serializers.CharField(source='user.name')
    phone_number = serializers.CharField(source='user.phone_number', required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = Organizer
        fields = ['id', 'name', 'email', 'username', 'phone_number', 'avatar', 'type', 'company_name', 'bank_account']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AdminUserQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(
        required=False,
        choices=['ALL', 'ADMIN', 'CUSTOMER', 'ORGANIZER'],
    )
    account_status = serializers.ChoiceField(
        required=False,
        choices=['ALL', 'ACTIVE', 'LOCKED'],
    )
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
    )


class AdminUserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()
    can_change_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'username', 'email', 'phone_number', 'avatar',
            'role', 'account_status', 'is_active', 'status', 'date_joined',
            'last_login', 'is_superuser', 'can_change_status',
        ]

    def get_role(self, user):
        # Staff và superuser luôn được hiển thị là Admin.
        if user.is_staff or user.is_superuser:
            return UserType.ADMIN
        return user.type

    def get_account_status(self, user):
        if user.is_active and user.status:
            return 'ACTIVE'
        return 'LOCKED'

    def get_can_change_status(self, user):
        request = self.context.get('request')
        is_current_user = bool(request and request.user.id == user.id)
        is_admin = (
            user.type == UserType.ADMIN
            or user.is_staff
            or user.is_superuser
        )
        return not is_current_user and not is_admin


class AdminUserDetailSerializer(AdminUserListSerializer):
    dob = serializers.DateField(read_only=True)
    customer_profile = serializers.SerializerMethodField()
    organizer_profile = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()

    class Meta(AdminUserListSerializer.Meta):
        fields = AdminUserListSerializer.Meta.fields + [
            'dob', 'customer_profile', 'organizer_profile', 'statistics',
        ]

    def get_customer_profile(self, user):
        try:
            customer = user.customer
        except Customer.DoesNotExist:
            return None

        return {'tier': customer.tier}

    def get_organizer_profile(self, user):
        try:
            organizer = user.organizer
        except Organizer.DoesNotExist:
            return None

        return {
            'company_name': organizer.company_name,
            'bank_account': organizer.bank_account,
        }

    def get_statistics(self, user):
        return self.context.get('statistics', {})


class AdminUserSummarySerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_organizers = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    total_locked = serializers.IntegerField()
