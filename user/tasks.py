from django.contrib.auth import get_user_model

from user.models import Post, User

from celery import shared_task


@shared_task
def create_post(user_id):
    user = get_user_model().objects.get(id=user_id)
    title = "New post"
    content = f"{title} from {user.username}"
    hashtag = "Celery"
    post = Post.objects.create(
        hashtag=hashtag,
        title=title,
        content=content,
        created_by=user
    )
    post.save()
    return post.id
