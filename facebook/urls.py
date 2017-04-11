"""facebook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.auth import views as auth_views
from UserDetail.views import UserProfileDetail,\
    ManageFriendRequest,\
    ManageFriends,\
    ManageFollowRequest,\
    PostList,\
    PostAction, \
    friends_list,\
    friendship_request_sent,\
    friendship_request_receive,\
    friendship_request_viewed, \
    friendship_request_rejected,\
    friendship_request_unrejected,\
    friendship_request_unread,\
    following,\
    followers

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^facebook/(?P<pk>\d+|None)/$',
        UserProfileDetail.as_view(),
        name=""),
    url(r'^facebook/manage_friend_request/(?P<pk>\d+|None)/$',
        ManageFriendRequest.as_view(),
        name="manage_friend_request"),
    url(r'^facebook/manage_friends/(?P<pk>\d+|None)/$',
        ManageFriends.as_view(),
        name="manage_friends"),
    url(r'^facebook/manage_follow_request/(?P<pk>\d+|None)/$',
        ManageFollowRequest.as_view(),
        name="manage_follow_request"),
    url(r'^facebook/post_list/(?P<pk>\d+|None)/$',
        PostList.as_view(),
        name="post_list"),
    url(r'^facebook/post_action/(?P<pk>\d+|None)/$',
        PostAction.as_view(),
        name="post_action"),
    url(r'^facebook/friends_list/$',
        friends_list,
        name="friends_list"),
    url(r'^facebook/friendship_request_sent/$',
        friendship_request_sent,
        name="friendship_request_sent"),
    url(r'^facebook/friendship_request_receive/$',
        friendship_request_receive,
        name="friendship_request_receive"),
    url(r'^facebook/friendship_request_viewed/$',
        friendship_request_viewed,
        name="friendship_request_viewed"),
    url(r'^facebook/friendship_request_rejected/$',
        friendship_request_rejected,
        name="friendship_request_rejected"),
    url(r'^facebook/friendship_request_unrejected/$',
        friendship_request_unrejected,
        name="friendship_request_unrejected"),
    url(r'^facebook/friendship_request_unread/$',
        friendship_request_unread,
        name="friendship_request_unread"),
    url(r'^facebook/following/$',
        following,
        name="following"),
    url(r'^facebook/followers/$',
        followers,
        name="followers"),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
