from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, full_name, mobile_number, password=None):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name,
            mobile_number=mobile_number,
            is_active=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, full_name, mobile_number, password):
        user = self.create_user(
            username=username,
            email=email,
            full_name=full_name,
            mobile_number=mobile_number,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)

    email_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "full_name", "mobile_number"]

    def __str__(self):
        return self.username
