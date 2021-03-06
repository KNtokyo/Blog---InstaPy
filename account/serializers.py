from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
from .utils import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=6)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, validated_data):
        # print(validated_data)
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return validated_data

    def create(self, validated_data):
        """This function is called when self.save() method is called"""
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code(email=user.email, activation_code=user.activation_code)
        return user


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.pop('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Не удаётся авторизоваться с введёнными данными.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Email и пароль обязательны для ввода.')
            raise serializers.ValidationError(msg, code='authorization')
        if user and user.is_active:
            refresh =  self.get_token(user)
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
            attrs['user'] = {'user_id':user.id, 'user_email': user.email}
        return attrs

# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(
#         label='Password',
#         style={'input_type': 'password'},
#         trim_whitespace=False
#     )
#
#     def validate(self, validated_data):
#         email = validated_data.get('email')
#         password = validated_data.get('password')
#
#         if email and password:
#             user = authenticate(request=self.context.get('request'),
#                                 email=email, password=password)
#             if not user:
#                 message = "I can't find user with this data "
#                 serializers.ValidationError(message, code='authorization')
#
#         else:
#             message = 'Must include "password" and "email"'
#             serializers.ValidationError(message, code='authorization')
#
#         validated_data['user'] = user
#         return validated_data