from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Post, Like, Comment
from user.permissions import IsAdminOrIsAuthenticatedReadOnly, IsCreatedOrReadOnly
from user.serializers import UserSerializer, UserDetailSerializer, UserListSerializer, UserFollowersSerializer, \
    PostSerializer, PostListSerializer, PostDetailSerializer, LikeSerializer, LikeListSerializer, CommentSerializer, \
    CommentListSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer

        if self.action == "list":
            return UserListSerializer

        if self.action in ("follow", "unfollow"):
            return UserFollowersSerializer

        return UserSerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("followers", "follows")
        email = self.request.query_params.get("email")
        username = self.request.query_params.get("username")

        if email:
            queryset = queryset.filter(email__icontains=email)

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="follow",
        permission_classes=(IsAuthenticated,)
    )
    def follow(self, request, pk=None):
        """Endpoint for users to follow other users"""
        user = self.get_object()
        follower = self.request.user

        if user != follower and follower not in user.followers.all():
            user.followers.add(follower)
            user.save()

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="unfollow",
        permission_classes=(IsAuthenticated,)
    )
    def unfollow(self, request, pk=None):
        """Endpoint for users to unfollow other users"""
        user = self.get_object()
        follower = self.request.user

        if user != follower and follower in user.followers.all():
            user.followers.remove(follower)
            user.save()

        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                description="Filter by email (ex. ?email=Youre@mail.com)"
            ),
            OpenApiParameter(
                name="username",
                type=str,
                description="Filter by username (ex. ?username=YourUsername)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action in ("update", "partial_update", "destroy"):
            return [IsCreatedOrReadOnly()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "like":
            return LikeSerializer

        if self.action == "add_comment":
            return CommentSerializer

        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("comments", "likes")

        hashtag = self.request.query_params.get("hashtag")
        username = self.request.query_params.get("username")

        if hashtag:
            queryset = queryset.filter(hashtag__icontains=hashtag)
        if username:
            queryset = queryset.filter(created_by=username)

        queryset = queryset.filter(
            Q(created_by=self.request.user)
            | Q(created_by__in=self.request.user.follows.all())
        )
        queryset = queryset.select_related("created_by")

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=(IsAuthenticated,)
    )
    def like(self, request, pk=None):
        """Endpoint for users to like posts"""
        post = self.get_object()
        user = self.request.user

        try:
            like = get_object_or_404(Like, post=post, user=user)
            like.delete()
        except Http404:
            Like.objects.create(post=post, user=user, is_liked=True)

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add_comment",
        permission_classes=(IsAuthenticated,)
    )
    def add_comment(self, request, pk=None):
        """Endpoint for users to comment posts"""
        post = self.get_object()
        user = self.request.user

        Comment.objects.create(
            post=post,
            user=user,
            content=request.data["content"]
        )

        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type=str,
                description="Filter by hashtag (ex. ?hashtag=YourHashtag)"
            ),
            OpenApiParameter(
                name="username",
                type=str,
                description="Filter by username (ex. ?username=YourUsername)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LikeListView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeListSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("post")
        user = self.request.user

        queryset = queryset.filter(user=user)

        return queryset


class CommentListViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("post")
        user = self.request.user

        queryset = queryset.filter(user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer

        if self.action == "retrieve":
            return CommentSerializer

        return CommentSerializer
