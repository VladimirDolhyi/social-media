from django.contrib import admin

from social_media.models import Post, Profile, Follow, Comment, Like

admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
