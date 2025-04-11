from rest_framework import serializers
from .models import *
import base64

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'date_of_birth']

    def create(self, validated_data):
        dob = validated_data.pop('date_of_birth')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user_profile = user.profile  # Created via signal
        user_profile.date_of_birth = dob
        user_profile.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = '__all__'

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

class ClubProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubProfile
        fields = '__all__'

class ClubAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubAdmin
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['file', 'file_type']

class PostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True)  # This will allow multiple media for one post
    
    class Meta:
        model = Post
        fields = ['owner', 'caption', 'tags', 'is_public', 'media']
    
    def create(self, validated_data):
        media_data = validated_data.pop('media', [])
        post = Post.objects.create(**validated_data)
        
        for media in media_data:
            PostMedia.objects.create(post=post, **media)
        
        return post

    def update(self, instance, validated_data):
        media_data = validated_data.pop('media', [])
        
        instance.caption = validated_data.get('caption', instance.caption)
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        instance.is_public = validated_data.get('is_public', instance.is_public)
        instance.save()

        # Handle media updates (if any)
        for media in media_data:
            PostMedia.objects.create(post=instance, **media)
        
        return instance


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
