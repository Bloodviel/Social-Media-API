from django.urls import include, path
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet

router = DefaultRouter()
router.register("users-list", UserViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "user"
