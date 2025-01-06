from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import OuterRef, Subquery, Max
from django.shortcuts import get_object_or_404, redirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from social_media.models import Profile, Follow, Post, PostReaction, Comment
from social_media.serializers import (
    ProfileSerializer,
    FollowSerializer,
    PostSerializer,
    LikeSerializer, CommentSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            username = self.request.query_params.get("username")
            if username:
                queryset = queryset.filter(username__icontains=username)
            return queryset.distinct()
        else:
            return self.queryset.filter(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by username (ex. ?username=name)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):

    def post(self, request, profile_id):
        profile_to_follow = get_object_or_404(Profile, id=profile_id)

        if request.user.profile == profile_to_follow:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_instance, created = Follow.objects.get_or_create(
            follower=request.user, followed=profile_to_follow.user
        )

        if created:
            return Response(
                {"message": f"You are now following"
                            f"{profile_to_follow.username}."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": "You are already following this user."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UnfollowUserView(APIView):

    def post(self, request, profile_id):
        profile_to_unfollow = get_object_or_404(Profile, id=profile_id)

        try:
            follow_instance = Follow.objects.get(
                follower=request.user, followed=profile_to_unfollow.user
            )
            follow_instance.delete()
            return Response(
                {"message": f"You have unfollowed"
                            f"{profile_to_unfollow.username}."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Follow.DoesNotExist:
            return Response(
                {"error": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FollowingListView(APIView):
    def get(self, request):
        following = request.user.following.all()
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


class FollowersListView(APIView):
    def get(self, request):
        followers = request.user.followers.all()
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)


User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):

        queryset = self.queryset.select_related("user")

        if self.action == "retrieve":
            user_posts = self.request.user.posts.all()
            following_users = User.objects.filter(
                followers__follower=self.request.user
            )
            following_posts = Post.objects.filter(user__in=following_users)
            combined_posts = user_posts | following_posts
            queryset = combined_posts.distinct()

        hashtag = self.request.query_params.get("hashtag")
        title = self.request.query_params.get("title")

        if hashtag:
            queryset = queryset.filter(hashtags__icontains=hashtag)

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type=OpenApiTypes.STR,
                description="Filter by hashtag (ex. ?hashtag=hello)",
            ),
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter by title (ex. ?title=good)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = LikeSerializer

    def get_queryset(self):
        user = self.request.user
        subquery = PostReaction.objects.filter(
            user=user,
            reaction=PostReaction.Likes.LIKE,
            post=OuterRef('post')
        ).order_by('-id')

        return PostReaction.objects.filter(
            id=Subquery(subquery.values('id'))
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            self.permission_denied(
                request, message="You do not have permission to delete this like."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            self.permission_denied(
                request, message="You do not have permission to update this comment."
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            self.permission_denied(
                request, message="You do not have permission to delete this comment."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
