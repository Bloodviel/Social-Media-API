from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from user.views import CreateUserView, ManageUserView, UserViewSet, LogoutView, PostViewSet, LikeListView

router = DefaultRouter()
router.register("users-list", UserViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("liked-posts/", LikeListView.as_view(), name="liked_posts")
]

app_name = "user"
