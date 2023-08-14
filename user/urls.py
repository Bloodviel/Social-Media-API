from django.urls import include, path
from rest_framework.routers import DefaultRouter

from user.views import CreateUserView, UserViewSet

router = DefaultRouter()
router.register("users-list", UserViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("", include(router.urls)),
]

app_name = "user"
