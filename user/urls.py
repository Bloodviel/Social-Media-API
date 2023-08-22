from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from social.views import LikeListView
from user.views import (
    CreateUserView,
    LogoutView,
    ManageUserView,
    UserViewSet,
)

router = DefaultRouter()
router.register("all", UserViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("liked-posts/", LikeListView.as_view(), name="liked-posts"),
] + router.urls

app_name = "user"
