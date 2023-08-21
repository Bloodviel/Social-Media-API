from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers

from user.models import Post, Like


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "get_followers",
            "get_followings",
            "image",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "bio",
            "is_staff"
        ]
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password()
            user.save()

        return user


class UserListSerializer(UserSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "image",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_staff",
        ]


class UserDetailSerializer(UserSerializer):
    followers = serializers.StringRelatedField(many=True)
    follows = serializers.StringRelatedField(many=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "get_followers",
            "followers",
            "get_followings",
            "follows",
            "image",
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "is_staff",
        ]


class UserFollowersSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["id", "followers"]


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            "image",
            "hashtag",
            "title",
            "content",
        ]


class PostListSerializer(PostSerializer):
    created_by = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "hashtag",
            "title",
            "created_by",
            "created_at",
            "get_comments",
            "get_likes",
        ]


class PostDetailSerializer(PostSerializer):
    created_by = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "image",
            "hashtag",
            "title",
            "content",
            "created_by",
            "created_at",
            "get_comments",
            "get_likes",
        ]


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ["id", "is_liked"]


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'email' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
