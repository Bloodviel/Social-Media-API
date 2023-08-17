from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Post
from user.permissions import IsAdminOrIsAuthenticatedReadOnly, IsCreatedOrReadOnly
from user.serializers import UserSerializer, UserDetailSerializer, UserListSerializer, UserFollowersSerializer, \
    PostSerializer, PostListSerializer, PostDetailSerializer


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

        if self.action == "following":
            return UserFollowersSerializer

        return UserSerializer

    def get_queryset(self):
        queryset = self.queryset
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
    def following(self, request, pk=None):
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

        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset

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

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
