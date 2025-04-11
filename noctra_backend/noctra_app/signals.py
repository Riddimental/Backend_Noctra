from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *

@receiver(post_save, sender=Club)
def add_creator_to_club_admin(sender, instance, created, **kwargs):
    if created:  # Only trigger when the Club is created
        # Get the user who created the club
        user = instance.created_by
        profile = UserProfile.objects.get(user=user)
        
        # Check if the user is a Club Admin or Super Admin
        if profile.role in ['club_admin', 'super_admin']:
            # Add this user as a ClubAdmin for the newly created club
            ClubAdmin.objects.create(user=user, club=instance)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
@receiver(post_save, sender=UserProfile)
def create_feed_for_user_profile(sender, instance, created, **kwargs):
    if created and not instance.feed:
        feed = Feed.objects.create(user=instance.user)
        instance.feed = feed
        instance.save()

@receiver(post_save, sender=ClubProfile)
def create_feed_for_club_profile(sender, instance, created, **kwargs):
    if created and not instance.feed:
        feed = Feed.objects.create(user=instance.club.created_by)
        instance.feed = feed
        instance.save()

