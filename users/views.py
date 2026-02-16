from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
from .utils import send_email_otp

from rest_framework.exceptions import ValidationError
from .serializers import VerifyEmailSerializer
from .models import User


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_email_otp(user)

        return Response({
            "message": "Verification code sent to your email"
        }, status=status.HTTP_201_CREATED)
    

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid email")

        if user.email_otp != otp:
            raise ValidationError("Invalid OTP")

        user.is_active = True
        user.email_otp = None
        user.otp_created_at = None
        user.save()

        return Response({
            "message": "Email verified successfully. You can now login."
        })

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        tokens = get_tokens_for_user(user)

        return Response({
            "user": {
                "username": user.username,
                "email": user.email,
            },
            "tokens": tokens
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "full_name": request.user.full_name,
            "email": request.user.email,
            "mobile_number" : request.user.mobile_number,
        })

