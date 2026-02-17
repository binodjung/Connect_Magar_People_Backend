from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, PendingUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "mobile_number",
            "password",
        ]

    def validate_email(self, value):
        return value.lower().strip()

    def create(self, validated_data):
        # Hash password before saving to PendingUser
        password = validated_data.pop('password')
        pending_user = PendingUser(**validated_data)
        # We manually hash the password because PendingUser is not an AbstractBaseUser
        from django.contrib.auth.hashers import make_password
        pending_user.password = make_password(password)
        pending_user.save()
        return pending_user
    

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        print(f"DEBUG: Attempting login. Input username/email: {data['username']}")
        
        username = data["username"]
        password = data["password"]

        # Check if input is an email
        if '@' in username:
            from .models import User
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
                print(f"DEBUG: Input is email. Resolved to username: {username}")
            except User.DoesNotExist:
                print("DEBUG: Input looks like email but no user found.")
                # We let it fail in authenticate, or raise here.
                # Let's let it proceed to authenticate which will fail.

        user = authenticate(
            username=username,
            password=password
        )

        if not user:
            # Check if user exists to give better debug info
            from .models import User
            try:
                u = User.objects.get(username=data["username"])
                print(f"DEBUG: User found but auth failed. Encrypted password in DB: {u.password}")
                print(f"DEBUG: Check password (raw): {data['password']}")
            except User.DoesNotExist:
                print("DEBUG: User does not exist at all.")
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            print("DEBUG: User exists but is_active=False")
            raise serializers.ValidationError("User account is disabled.")

        return user
