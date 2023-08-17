from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.permissions import IsAdminOrIsAuthenticatedReadOnly
from user.serializers import UserSerializer, UserDetailSerializer, UserListSerializer, UserFollowersSerializer


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
