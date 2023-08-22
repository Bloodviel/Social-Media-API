from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from user.views import (
    CreateUserView,
    CommentListViewSet,
    LikeListView,
    LogoutView,
    ManageUserView,
    PostViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users-list", UserViewSet)
router.register("posts", PostViewSet)
router.register("commented-posts", CommentListViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("liked-posts/", LikeListView.as_view(), name="liked-posts"),
]

app_name = "user"
