from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError

from django.db import transaction

from .serializers import RegisterSerializer, LoginSerializer, VerifyEmailSerializer
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
                "full_name": user.full_name,
                "mobile_number": user.mobile_number,
                "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
            },
            "tokens": tokens
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response({
            "username": request.user.username,
            "full_name": request.user.full_name,
            "email": request.user.email,
            "mobile_number" : request.user.mobile_number,
            "profile_picture": request.build_absolute_uri(request.user.profile_picture.url) if request.user.profile_picture else None,
        })

    def patch(self, request):
        user = request.user
        data = request.data
        print(f"DEBUG: Profile Patch Data: {data}")
        print(f"DEBUG: Profile Patch Files: {request.FILES}")
        
        # Email is NOT updateable
        if 'email' in data:
            return Response({"error": "Email cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)
            
        if data.get('full_name'):
            user.full_name = data['full_name']
        if data.get('mobile_number'):
            user.mobile_number = data['mobile_number']
        if data.get('username'):
            new_username = data['username']
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
             
        try:
            user.save()
        except Exception as e:
            if "mobile_number" in str(e).lower():
                return Response({"error": "This mobile number is already registered with another account."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": f"Database error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "mobile_number" : user.mobile_number,
            "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
            "message": "Profile updated successfully"
        })

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            send_email_otp(user)
            return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # We explicitly say user doesn't exist as requested by user
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

class VerifyResetOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        otp = str(request.data.get('otp', ''))
        try:
            user = User.objects.get(email=email)
            if user.email_otp == otp:
                return Response({"message": "OTP verified."}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        otp = str(request.data.get('otp', ''))
        new_password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not otp or not new_password:
            return Response({"message": "Password and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
             return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.email_otp == otp:
                user.set_password(new_password)
                user.email_otp = None  # Clear OTP after use
                user.save()
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not current_password or not new_password:
             return Response({"message": "Current and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
             
        if new_password != confirm_password:
             return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(current_password):
            return Response({"message": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

