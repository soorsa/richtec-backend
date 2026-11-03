
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.urls import reverse
from .utils import send_forgot_password_email

from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    def create(self, validated_data):
        role = validated_data.pop("role", None)
        user = User.objects.create_user(**validated_data)
        if role == "admin" or role == "staff":
            user.is_staff=True
            user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Incorrect email or password')
            if not user.is_active:
                raise serializers.ValidationError('Account disabled')
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

        attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields='__all__'
        # fields = ('id', 'email', 'username', 'first_name', 'last_name', 
        #          'phone_number', 'profile_picture', 'bio', 'date_of_birth', 
        #          'is_verified', 'created_at')
        read_only_fields = ('id', 'email', 'role', 'created_at', 'is_verified')

class ChangePasswordSerializer(serializers.Serializer):
    # old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            request = self.context.get("request")
            domain = "https://richtecafrica.com"

            reset_link = f"{domain}/reset-password/{uid}/{token}/"

            # send email (use your resend function)
            send_forgot_password_email(user, reset_link)

        return data


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(id=uid)

            if not PasswordResetTokenGenerator().check_token(user, data["token"]):
                raise serializers.ValidationError("Invalid or expired token")

            user.set_password(data["password"])
            user.save()

        except Exception:
            raise serializers.ValidationError("Invalid reset link")

        return user