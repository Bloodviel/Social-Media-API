from rest_framework.routers import DefaultRouter

from social.views import PostViewSet, CommentListViewSet

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("commented-posts", CommentListViewSet)

urlpatterns = [

] + router.urls

app_name = "social"
