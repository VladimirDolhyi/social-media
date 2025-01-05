from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


class Post(models.Model):
    user = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE
    )
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.CharField(max_length=255, blank=True)


class Comment(models.Model):
    user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    content = models.TextField()


class Like(models.Model):
    user = models.ForeignKey(
        User, related_name="likes", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, related_name="likes", on_delete=models.CASCADE
    )
