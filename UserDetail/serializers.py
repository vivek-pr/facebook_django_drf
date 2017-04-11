from rest_framework import serializers
from django.contrib.auth.models import User
from UserDetail.models import UserProfile, FriendshipRequest, PostAction, FacebookPost, Follow, Friend

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        depth = 1
        fields = ('user',
                  'gender',
                  'mobile_no',
                  'relation_ship_status',
                  'about_you',
                  'cover_pic',
                  'profile_pic')


class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendshipRequest
        fields = ('from_user',
                  'to_user',
                  'message')


class PostActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAction
        fields = ('action_type',
                  'user',
                  'post',
                  'comments')


class FacebookPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPost
        fields = ('owner',
                  'message',
                  'picture',
                  'video',
                  'link',
                  'post_type',
                  'caption',
                  'description',
                  'story',
                  'privacy',
                  'place_long',
                  'place_lat')


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower',
                  'followee')


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ('from_user',
                  'to_user',
                  'created')
