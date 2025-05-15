from datetime import date
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os


# Upload paths
def upload_profile_pic(instance, filename):
    return f'images/profile_pictures/{instance.user.username}/{uuid.uuid4().hex}.{filename.split(".")[-1]}'

def upload_club_profile_pic(instance, filename):
    return f'images/club_profile_pictures/{instance.name}/{uuid.uuid4().hex}.{filename.split(".")[-1]}'

def upload_cover_pic(instance, filename):
    return f'images/cover_pictures/{instance.user.username}/{uuid.uuid4().hex}.{filename.split(".")[-1]}'

def upload_club_cover_pic(instance, filename):
    return f'images/club_cover_pictures/{instance.club.name}/{uuid.uuid4().hex}.{filename.split(".")[-1]}'


class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Feed"


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('club_owner', 'Club Owner'),
        ('club_admin', 'Club Admin'),
    ]

    SYSTEM_ROLE_CHOICES = [
        ('regular', 'Regular'),
        ('super_admin', 'Super Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    system_role = models.CharField(max_length=20, choices=SYSTEM_ROLE_CHOICES, default='regular')
    profile_pic = models.ImageField(
        upload_to=upload_profile_pic, null=True, blank=True,
        default='images/profile_pictures/default_profile.jpg'
    )
    cover_pic = models.ImageField(
        upload_to=upload_cover_pic, null=True, blank=True,
        default='images/cover_pictures/default_cover.jpg'
    )
    playlist = models.URLField(max_length=500, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_vip = models.BooleanField(default=False)
    bio = models.TextField(max_length=255, null=True, blank=True)
    publicProfile = models.BooleanField(default=True)
    anonymous = models.BooleanField(default=False)
    feed = models.OneToOneField(Feed, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def username(self):
        return self.user.username

    def get_profile_pic_url(self):
        return self.profile_pic.url if self.profile_pic else '../media/images/profile_pictures/default_profile.jpg'

    def get_cover_pic_url(self):
        return self.cover_pic.url if self.cover_pic else '../media/images/cover_pictures/default_cover.jpg'

    def get_user_type_display_name(self):
        return dict(self._meta.get_field('user_type').choices).get(self.user_type)

    def get_system_role_display_name(self):
        return dict(self._meta.get_field('system_role').choices).get(self.system_role)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display_name()})"

class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    company_main_location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(
        upload_to=upload_club_profile_pic, null=True, blank=True,
        default='images/profile_pictures/default_profile.jpg'
    )
    admins = models.ManyToManyField(User, related_name='admin_clubs', blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_clubs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClubProfile(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE, related_name='club_profile')
    cover_pic = models.ImageField(
        upload_to=upload_club_cover_pic, null=True, blank=True,
        default='images/cover_pictures/default_cover.jpg'
    )
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    feed = models.OneToOneField(Feed, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.PositiveIntegerField()
    available_tickets = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(available_tickets__lte=models.F('total_tickets')), name='available_tickets_check')
        ]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=255, unique=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Ticket {self.id} ({self.event.name if self.event else 'No event'})"


class VIPSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_subscription')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def is_active(self):
        return self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.user.username} VIP until {self.end_date}"
    

def post_media_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    user = instance.post.owner.username
    base = 'other'

    # Determine media type and folder
    if ext.lower() in ['jpg', 'jpeg', 'png', 'gif']:
        base = f'images/posts/{user}'
    elif ext.lower() in ['mp4', 'mov', 'avi']:
        base = f'videos/posts/{user}'
    elif ext.lower() in ['mp3', 'wav']:
        base = f'other/audios/{user}'
    elif ext.lower() in ['pdf', 'docx']:
        base = f'other/documents/{user}'
    # make an organized name for the file
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(base, filename)


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    caption = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    tags = models.ManyToManyField("Tag", related_name='posts', blank=True)
    mentions = models.ManyToManyField(User, related_name="mentioned_posts", blank=True)
    original_post = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="reposts")

    def __str__(self):
        return f"{self.owner.username} - {self.caption} - {self.created_at.strftime('%Y-%m-%d')}"

    def mentioned_usernames(self):
        return [user.username for user in self.mentions.all()]


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to=post_media_upload_path)
    file_type = models.CharField(max_length=10)  # image, video, audio, etc.

    def save(self, *args, **kwargs):
        # Automatically determine media type (optional, bonus)
        if not self.file_type:
            if self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                self.file_type = 'image'
            elif self.file.name.lower().endswith(('.mp4', '.mov', '.avi')):
                self.file_type = 'video'
            elif self.file.name.lower().endswith(('.mp3', '.wav')):
                self.file_type = 'audio'
            else:
                self.file_type = 'other'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Media for Post {self.post.id}"
    
class Mention(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_mention')
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentioned_in_posts')
    mentioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentioned_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentioned_by.username} mentioned {self.mentioned_user.username} in Post {self.post.id}"


    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    def __str__(self):
        return f"{self.author.username} comment on Post {self.post.id}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.user.username}"


class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='following')
    following_user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='followers')
    following_club = models.ForeignKey(ClubProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='club_followers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} follows {self.following_user or self.following_club}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    table_number = models.IntegerField()
    group_size = models.PositiveIntegerField()
    special_requests = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} reservation for {self.event.name}"
