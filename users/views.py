from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction

from .serializers import RegisterSerializer, LoginSerializer
from .utils import send_email_otp

from rest_framework.exceptions import ValidationError
from .serializers import VerifyEmailSerializer
from .models import User, PendingUser


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email', '').lower().strip() # Normalize email

        print(f"DEBUG: Registering username: {username}, email: {email}")

        # Cleanup: Delete any "Stuck" Inactive users in the main table
        # This fixes the issue where a user is created but verification failed/stalled
        User.objects.filter(username=username, is_active=False).delete()
        User.objects.filter(email=email, is_active=False).delete()

        # Check if ACTIVE user already exists
        if User.objects.filter(username=username).exists() or \
           User.objects.filter(email=email).exists():
            return Response({"message": "User with this username or email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear any existing PendingUser to allow re-registration
        PendingUser.objects.filter(email=email).delete()
        PendingUser.objects.filter(username=username).delete()

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save to PendingUser
        pending_user = serializer.save()

        # Send OTP (modified to accept PendingUser)
        send_email_otp(pending_user)

        return Response({
            "message": "Verification code sent to your email"
        }, status=status.HTTP_201_CREATED)
    

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("DEBUG: VerifyEmailView called")
        print(f"DEBUG: Request Data: {request.data}")
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip() # Normalize email
        otp = serializer.validated_data["otp"]
        
        print(f"DEBUG: Verifying for email: '{email}' with OTP: '{otp}'")

        try:
            with transaction.atomic():
                try:
                    # Debug: List all PendingUsers to see if it's there
                    # all_pending = PendingUser.objects.values('email', 'otp')
                    # print(f"DEBUG: Current PendingUsers: {list(all_pending)}")
                    
                    pending_user = PendingUser.objects.get(email=email)
                except PendingUser.DoesNotExist:
                    print(f"DEBUG: PendingUser not found for '{email}'")
                    # Check if user is already verified (Active User)
                    if User.objects.filter(email=email, is_active=True).exists():
                         return Response({"message": "Email already verified. Please login."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # If user exists but is Inactive, it means registration is broken/stuck
                    if User.objects.filter(email=email, is_active=False).exists():
                         # We deleted the stuck user in RegisterView, so this shouldn't happen unless they didn't re-register
                        return Response({"message": "Registration session expired. Please Register again."}, status=status.HTTP_400_BAD_REQUEST)
                        
                    raise ValidationError("Registration session expired or invalid email.")

                if pending_user.otp != otp:
                     raise ValidationError("Invalid OTP")
                
                print(f"DEBUG: Creating user for {email}")
                # Create the actual User
                user = User.objects.create_user(
                    username=pending_user.username,
                    email=pending_user.email,
                    full_name=pending_user.full_name,
                    mobile_number=pending_user.mobile_number,
                    password=None  # Don't set password via create_user to avoid double hashing
                )
                
                # Assign the already hashed password from PendingUser
                user.password = pending_user.password
                user.is_active = True
                user.save()
                
                print("DEBUG: User created and activated")

                # Delete PendingUser
                pending_user.delete()

                return Response({
                    "message": "Email verified successfully.",
                    "tokens": get_tokens_for_user(user)
                }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"DEBUG: Verify failed: {e}")
            raise e

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

    def patch(self, request):
        user = request.user
        data = request.data
        
        # Email is NOT updateable
        if 'email' in data:
            return Response({"error": "Email cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'mobile_number' in data:
            user.mobile_number = data['mobile_number']
        if 'username' in data:
            new_username = data['username']
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username
             
        user.save()
        return Response({
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "mobile_number" : user.mobile_number,
            "message": "Profile updated successfully"
        })

