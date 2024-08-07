from django.db import models
from djongo import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import make_password, check_password

# class User(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True, default='default@example.com')  
#     username = models.CharField(max_length=50, unique=True)
#     password = models.CharField(max_length=255)  # TODO use a more secure field for passwords

#     def save(self, *args, **kwargs):
#         # Hash the password before saving
#         self.password = make_password(self.password)
#         super(User, self).save(*args, **kwargs)

#     def check_password(self, raw_password):
#         return check_password(raw_password, self.password)

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)
    


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='default@example.com')  
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # TODO use a more secure field for passwords
    role = models.CharField(max_length=50, default='instructor')  # Add a 'role' field

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    course_description = models.TextField(null=True, blank=True)
    course_thumbnail_url = models.URLField()
    course_tags = models.JSONField(default=None, null=True)
    course_length = models.PositiveIntegerField(default=0)

class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=255)
    topic_asset_urls = models.JSONField()
    topic_asset_type = models.JSONField()
    topic_length = models.PositiveIntegerField()

class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_name = models.CharField(max_length=255)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50)
    asset_url = models.URLField()
    asset_length = models.PositiveIntegerField()
    asset_thumbnail = models.URLField()

class BulkUpload(models.Model):
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('transcoding', 'Transcoding'),
        ('processed', 'Processed'),
    ]

    bulk_upload_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    bulk_upload_s3_url_temporary = models.URLField()
    bulk_upload_name = models.CharField(max_length=255)
    bulk_upload_time_date = models.DateTimeField(auto_now_add=True)
    bulk_upload_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
