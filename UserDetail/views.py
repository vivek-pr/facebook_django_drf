# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from UserDetail.models import UserProfile,\
    FriendshipRequest,\
    PostManager,\
    Friend,\
    Follow, FacebookPost
from UserDetail.serializers import UserDetailSerializer,\
    FriendshipRequestSerializer,\
    PostActionSerializer,\
    FacebookPostSerializer,\
    FollowSerializer,\
    FriendSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


class UserProfileDetail(APIView):
    """
    Create, Retrieve, update or delete a user detail instance.
    """
    def get_object(self, pk):
        try:
            return UserProfile.objects.get(pk=pk, user__is_active=True)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """ Get User Details"""
        user_detail = self.get_object(pk)
        serializer = UserDetailSerializer(user_detail)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Update User Details"""
        user_detail = self.get_object(pk)
        serializer = UserDetailSerializer(user_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """ Delete User"""
        user_detail = self.get_object(pk)
        user_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageFriendRequest(APIView):
    """
    Retrieve, accept, cancel or delete a Friendship Request  instance.
    """
    def get_object(self, pk):
        try:
            return FriendshipRequest.objects.get(pk=pk)
        except FriendshipRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """ get the request detail"""
        friend_ship = self.get_object(pk)
        friend_ship.mark_viewed()
        serializer = FriendshipRequestSerializer(friend_ship)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ approve or cancel the request"""
        friend_ship = self.get_object(pk)
        request_type = request.PUT.get('request')
        serializer = FriendshipRequestSerializer(friend_ship)
        if request_type == 'Accept':
            friend_ship.accept()
        else:
            friend_ship.reject()
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        """  cancel or delete the request"""
        friend_ship = self.get_object(pk)
        friend_ship.cancel()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageFriends(APIView):
    """
    Give a friend request
    """

    def post(self, request, pk):
        """ Giving friend request"""
        serializer = FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Friend.objects.add_friend(serializer['from_user'], serializer['to_user'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """ Delete existing Friend"""
        serializer = FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Friend.objects.remove_friend(serializer['from_user'], serializer['to_user'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ManageFollowRequest(APIView):
    """
    Give a friend request or delete a existing friend
    """

    def post(self, request, pk):
        """ Giving friend request"""
        serializer = FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Follow.objects.add_follower(serializer['follower'], serializer['followee'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ Delete existing Friend"""
        serializer = FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Follow.objects.remove_follower(serializer['follower'], serializer['followee'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PostList(APIView):
    """
    List all Post, or create, update, delete a new post.
    """

    def get_object(self, pk):
        try:
            return FacebookPost.objects.get(pk=pk)
        except FacebookPost.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        posts = FacebookPost.objects.profile_post(request.user)
        serializer = FacebookPostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        serializer = FacebookPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = FacebookPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostAction(APIView):
    """
    Get all action for a certain post, do action on the post
    """

    def get(self, request, pk, format=None):
        snippets = FacebookPost.objects.post_detail(pk)
        serializer = PostActionSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        serializer = PostActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def friends_list(request):
    total_friends = Friend.objects.friends(request.user)
    serializer = FriendSerializer(total_friends, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_sent(request):
    friend_request_sent = Friend.objects.sent_requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_sent, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_receive(request):
    friend_request_receive = Friend.objects.requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_receive, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_viewed(request):
    friend_request_viewed = Friend.objects.read_requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_viewed, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_rejected(request):
    friend_request_rejected = Friend.objects.rejected_requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_rejected, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_unrejected(request):
    friend_request_unrejected = Friend.objects.unrejected_requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_unrejected, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def friendship_request_unread(request):
    friend_request_unread = Friend.objects.unread_requests(request.user)
    serializer = FriendshipRequestSerializer(friend_request_unread, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def following(request):
    follow_list = Follow.objects.following(request.user)
    serializer = FollowSerializer(follow_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def followers(request):
    follow_list = Follow.objects.followers(request.user)
    serializer = FollowSerializer(follow_list, many=True)
    return Response(serializer.data)
