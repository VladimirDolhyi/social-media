from django.contrib import admin
from django.contrib.auth.models import Group

from social_media.models import Post, Profile, Follow, Comment, PostReaction

admin.site.unregister(Group)
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostReaction)
