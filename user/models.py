import os.path
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{ext}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    username = models.CharField(max_length=60, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    bio = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to=user_image_file_path)
    followers = models.ManyToManyField(
        "User",
        default=0,
        related_name="follows",
        symmetrical=False
    )

    class Meta:
        ordering = ["first_name"]

    @property
    def get_followers(self):
        return self.followers.count()

    @property
    def get_followings(self):
        return self.follows.count()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


def post_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{ext}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    hashtag = models.CharField(max_length=63)
    title = models.CharField(max_length=63)
    content = models.TextField()
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_comments(self):
        return self.comments.count()

    @property
    def get_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.content}"


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="likes",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="likes",
        on_delete=models.CASCADE
    )
    is_liked = models.BooleanField()

    class Meta:
        unique_together = ("user", "post")
