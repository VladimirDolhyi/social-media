from django.urls import path, include
from rest_framework import routers

from social_media.views import (
    ProfileViewSet,
    FollowUserView,
    UnfollowUserView,
    FollowingListView,
    FollowersListView,
    PostViewSet,
    LikeViewSet,
    CommentViewSet,
)

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("likes", LikeViewSet)
router.register("comments", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "follow/<int:profile_id>/",
        FollowUserView.as_view(),
        name="follow_user"
    ),
    path(
        "unfollow/<int:profile_id>/",
        UnfollowUserView.as_view(),
        name="unfollow_user"
    ),
    path("following/", FollowingListView.as_view(), name="following_list"),
    path("followers/", FollowersListView.as_view(), name="followers_list"),
]

app_name = "social_media"
