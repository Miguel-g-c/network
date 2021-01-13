from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete = models.CASCADE, related_name = "user"
    )

    followers = models.ManyToManyField(
        User, blank = True, related_name = "followers"
    )
    following = models.ManyToManyField(
        User, blank = True, related_name = "following"
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "followers": [user for user in self.followers.all()],
            "following": [user for user in self.following.all()],
            "followers_number": self.followers.all().count(),
            "following_number": self.following.all().count()
        }

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete = models.CASCADE, related_name = "author"
    )

    post = models.CharField(max_length = 280)
    timestamp = models.DateTimeField(auto_now_add = True)
    likes = models.ManyToManyField(User, blank = True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "post": self.post,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
            "likes": self.likes.all().count(),
            "liking": [user.username for user in self.likes.all()]
        }

    def __str__(self):
        return f"{self.user.username} post at {self.timestamp.strftime('%m/%d/%Y, %H:%M:%S')}"
