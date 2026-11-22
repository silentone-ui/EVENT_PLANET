from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(
        choices=User.RoleChoices.choices,
        default=User.RoleChoices.PARTICIPANT
    )

    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'password', 'role']

    def validate_phone(self, value):
        if len(value) != 11 or not value.startswith('09') or not value.isdigit():
            raise serializers.ValidationError('شماره موبایل باید ۱۱ رقم و با 09 شروع شود.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data['phone'] = self.user.phone
        data['role'] = self.user.role
        data['first_name'] = self.user.first_name
        return data