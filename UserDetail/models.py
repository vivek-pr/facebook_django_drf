from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q

GENDER = (('M', 'MALE'), ('F', 'FEMALE'))
RELATION = (('S', 'Single'), ('M', 'Married'), ('C', 'Complicated'))
TYPE = (('PIC', 'Picture'), ('VID', 'Video'), ('URL', 'Url'))
PRIVACY = (('ME', 'Me'), ('FND', 'Friends'), ('ALL', 'All'))
ACTION = (('L', 'Like'), ('S', 'Share'), ('C', 'Comments'))


class FriendshipRequest(models.Model):
    """ Model to represent friendship requests """
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent')
    to_user = models.ForeignKey(User, related_name='friendship_requests_received')

    message = models.TextField(blank=True)

    created = models.DateTimeField(default=timezone.now)
    rejected = models.DateTimeField(blank=True, null=True)
    viewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Friendship Request'
        verbose_name_plural = 'Friendship Requests'
        unique_together = ('from_user', 'to_user')

    def __unicode__(self):
        return "User #%s friendship requested #%s" % (self.from_user_id, self.to_user_id)

    def accept(self):
        """ Accept this friendship request """
        relation1 = Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )

        relation2 = Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user
        )

        self.delete()

        # Delete any reverse requests
        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()
        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = timezone.now()
        self.save()

    def cancel(self):
        """ cancel this friendship request """
        self.delete()
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        self.save()
        return True


class FriendshipManager(models.Manager):
    """ Friendship manager """

    def friends(self, user):
        """ Return a list of all friends """
        qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
        friends = [u.from_user for u in qs]
        return friends

    def requests(self, user):
        """ Return a list of friendship requests """

        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user).all()
        requests = list(qs)
        return requests

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
             from_user=user).all()
        requests = list(qs)
        return requests

    def unread_requests(self, user):
        """ Return a list of unread friendship requests """

        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=True).all()
        unread_requests = list(qs)
        return unread_requests

    def unread_request_count(self, user):
        """ Return a count of unread friendship requests """

        count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=True).count()
        return count

    def read_requests(self, user):
        """ Return a list of read friendship requests """

        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=False).all()
        read_requests = list(qs)
        return read_requests

    def rejected_requests(self, user):
        """ Return a list of rejected friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            rejected__isnull=False).all()
        rejected_requests = list(qs)
        return rejected_requests

    def unrejected_requests(self, user):
        """ All requests that haven't been rejected """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            rejected__isnull=True).all()
        unrejected_requests = list(qs)
        return unrejected_requests

    def unrejected_request_count(self, user):
        """ Return a count of unrejected friendship requests """
        count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                rejected__isnull=True).count()
        return count

    def add_friend(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise IntegrityError("Users are already friends")

        if message is None:
            message = ''

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
        )

        if created is False:
            raise IntegrityError("Friendship already requested")

        if message:
            request.message = message
            request.save()
        return request

    def remove_friend(self, from_user, to_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user) |
                Q(to_user=from_user, from_user=to_user)
            ).distinct().all()

            if qs:
                qs.delete()
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        try:
            Friend.objects.get(to_user=user1, from_user=user2)
            return True
        except Friend.DoesNotExist:
            return False


class Friend(models.Model):
    """ Model to represent Friendships """
    to_user = models.ForeignKey(User, related_name='friends')
    from_user = models.ForeignKey(User, related_name='_unused_friend_relation')
    created = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        verbose_name = 'Friend'
        verbose_name_plural = 'Friends'
        unique_together = ('from_user', 'to_user')

    def __unicode__(self):
        return "User #%s is friends with #%s" % (self.to_user_id, self.from_user_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)


class FollowingManager(models.Manager):
    """ Following manager """

    def followers(self, user):
        """ Return a list of all followers """
        qs = Follow.objects.filter(followee=user).all()
        followers = [u.follower for u in qs]
        return followers

    def following(self, user):
        """ Return a list of all users the given user follows """
        qs = Follow.objects.filter(follower=user).all()
        following = [u.followee for u in qs]
        return following

    def add_follower(self, follower, followee):
        """ Create 'follower' follows 'followee' relationship """
        if follower == followee:
            raise ValidationError("Users cannot follow themselves")

        relation, created = Follow.objects.get_or_create(follower=follower, followee=followee)

        if created is False:
            raise IntegrityError("User '%s' already follows '%s'" % (follower, followee))
        return relation

    def remove_follower(self, follower, followee):
        """ Remove 'follower' follows 'followee' relationship """
        try:
            rel = Follow.objects.get(follower=follower, followee=followee)
            rel.delete()
            return True
        except Follow.DoesNotExist:
            return False

    def follows(self, follower, followee):
        """ Does follower follow followee? Smartly uses caches if exists """

        try:
            Follow.objects.get(follower=follower, followee=followee)
            return True
        except Follow.DoesNotExist:
            return False


class Follow(models.Model):
    """ Model to represent Following relationships """
    follower = models.ForeignKey(User, related_name='following')
    followee = models.ForeignKey(User, related_name='followers')
    created = models.DateTimeField(default=timezone.now)

    objects = FollowingManager()

    class Meta:
        verbose_name = 'Following Relationship'
        verbose_name_plural = 'Following Relationships'
        unique_together = ('follower', 'followee')

    def __unicode__(self):
        return "User #%s follows #%s" % (self.follower_id, self.followee_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.follower == self.followee:
            raise ValidationError("Users cannot follow themselves.")
        super(Follow, self).save(*args, **kwargs)

class PostManager(models.Manager):

    def wall_post(self, user):
        qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
        friends = [u.from_user for u in qs]
        friends.append(user)
        return FacebookPost.objects.filter(owner__in=friends)

    def profile_post(self, user):
        return FacebookPost.objects.filter(owner=user)

    def post_detail(self, post):
        return PostAction.objects.select_related('user', 'post').filter(post=post)

    

class FacebookPost(models.Model):
    # Contains in data an array of objects, each with the name and Facebook id of the user
    owner = models.ForeignKey(User)

    message = models.TextField(help_text='The message')

    created_time = models.DateTimeField(help_text='The time the post was initially published', db_index=True)
    updated_time = models.DateTimeField(null=True, help_text='The time of the last comment on this post')

    picture = models.FileField(help_text='If available, a link to the picture included with this post')
    video = models.FileField(help_text='A URL to a Flash movie or video file to be embedded within the post')
    link = models.URLField(max_length=1500, help_text='The link attached to this post')
    post_type = models.CharField(max_length=10, db_index=True, choices=TYPE,
                                 help_text='A string indicating the type for this post (including link, photo, video)')
    caption = models.TextField(help_text='The caption of the link (appears beneath the link name)')
    description = models.TextField(help_text='A description of the link (appears beneath the link caption)')
    story = models.TextField(help_text='Text of stories not intentionally generated by users, such as those '
                                       'generated when two users become friends; you must have the "Include recent '
                                       'activity stories" migration enabled in your app to retrieve these stories')
    # object containing the value field and optional friends, networks, allow, deny and description fields.
    privacy = models.CharField(max_length=10, null=True, choices=PRIVACY, help_text='The privacy settings of the Post')
    place_long = models.CharField(max_length=10, null=True, help_text='Location associated with a Post, if any lattitude')

    place_lat = models.CharField(max_length=10, null=True, help_text='Location associated with a Post, if any longitude')
    objects = PostManager()
    class Meta:
        verbose_name = 'Facebook post'
        verbose_name_plural = 'Facebook posts'

    def __unicode__(self):
        return self.message or self.story


class PostAction(models.Model):
    action_type = models.CharField(max_length=10, db_index=True, choices=ACTION)
    user = models.ForeignKey(User)
    post = models.ForeignKey(FacebookPost)
    comments = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Post Action"
        verbose_name_plural = "Post Actions"

    def __unicode__(self):
        return self.user


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    gender = models.CharField(choices=GENDER, max_length=5, blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    relation_ship_status = models.CharField(choices=RELATION, max_length=5, blank=True, null=True)
    about_you = models.TextField(blank=True, null=True)
    cover_pic = models.ForeignKey(FacebookPost, related_name="cover_pic", blank=True, null=True)
    profile_pic = models.ForeignKey(FacebookPost, related_name="profile_pic", blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __unicode__(self):
        return "User #%s #%s registered" % (self.user__first_name, self.user__last_name)

    def save(self, *args, **kwargs):
        if self.cover_pic and self.cover_pic.post_type != 'PIC':
            raise ValidationError("Only pic allowed for cover pic")
        elif self.profile_pic and self.profile_pic.post_type != 'PIC':
            raise ValidationError("Only pic allowed for cover pic")
        else:
            super(UserProfile, self).save(*args, **kwargs)