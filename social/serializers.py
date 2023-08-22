from rest_framework import serializers

from social.models import Comment, Like, Post


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
            "comments_count",
            "likes_count",
        ]


class PostDetailSerializer(PostSerializer):
    created_by = serializers.CharField(
        source="created_by.username",
        read_only=True
    )
    comments = serializers.StringRelatedField(many=True)

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
            "comments_count",
            "comments",
            "likes_count",
        ]


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ["id", "is_liked"]


class LikeListSerializer(serializers.ModelSerializer):
    post = PostSerializer(many=False, read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post"]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "content"]


class CommentListSerializer(serializers.ModelSerializer):
    post = PostSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "post", "content"]
