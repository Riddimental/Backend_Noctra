from datetime import date
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User  # Import the default User model
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic_url = models.URLField(max_length=500, null=True, blank=True, default='/media/images/profile_pictures/pfpic4.jpeg')
    cover_pic_url = models.URLField(max_length=500, null=True, blank=True, default='/media/images/cover_pictures/coverpic2.jpeg')
    date_of_birth = models.DateField(null=True, blank=True)
    is_vip = models.BooleanField(default=False)
    bio = models.TextField(max_length=255, null=True, blank=True)
    #id_verification_url = models.URLField(max_length=500, null=True, blank=True)
    role = models.CharField(
        max_length=20, 
        choices=[('customer', 'Customer'), ('club_admin', 'Club Admin'), ('club_owner', 'Club Owner'), ('super_admin', 'Super Admin')], 
        default='customer'
    )
    feed = models.OneToOneField('Feed', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def username(self):
        """Returns the associated user's username."""
        return self.user.username

    def get_profile_pic_url(self):
        return self.profile_pic_url or '/media/public/default_profile.jpg'

    def get_cover_pic_url(self):
        return self.cover_pic_url or '/media/public/default_cover.jpg'

    def get_role_display_name(self):
        return dict(self._meta.get_field('role').choices).get(self.role)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display_name()})"




class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feed {self.user.username}"

class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    main_location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)  # Store URL of club image
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_clubs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ClubAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # one admin can manage one or many clubs
    club = models.ManyToManyField(Club, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.id}"

class ClubProfile(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE)
    profile_pic = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    feed = models.OneToOneField(Feed, on_delete=models.CASCADE, null=True, blank=True)
    managed_by = models.ManyToManyField(ClubAdmin, related_name='managed_clubs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.name
    
class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=255, unique=True)  # Store generated QR code
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Ticket {self.id} for {self.event.name}"
    
class VIPSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_subscription')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()  # Required for expiration

    def is_active(self):
        return self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.user.username} VIP until {self.end_date}"


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('story', 'Story'),
        ('promo', 'Promo'),  # Only for clubs
        ('menu', 'Menu'),  # Only for clubs
        ('product', 'Product')  # Only for clubs
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='posts')
    user_profile = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    club_profile = models.ForeignKey(ClubProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    content_type = models.CharField(max_length=10, choices=POST_TYPES)
    text = models.TextField(null=True, blank=True)
    media_url = models.URLField(null=True, blank=True)  # Used for images/videos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user_profile or self.club_profile} - {self.content_type}"

class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='following')
    following_user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='followers')
    following_club = models.ForeignKey(ClubProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='club_followers')  # Renamed related_name for clarity
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} follows {self.following_user or self.following_club}"

class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.post}"

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.PositiveIntegerField()
    available_tickets = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(available_tickets__lte=models.F('total_tickets')), name='available_tickets_check')
        ]

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
    group_size = models.PositiveIntegerField()  # New field
    special_requests = models.TextField(null=True, blank=True)  # New field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.event.name}"
