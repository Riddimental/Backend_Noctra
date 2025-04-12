from django.db import IntegrityError
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
        
class TagListSerializer(serializers.ListSerializer):
    def to_internal_value(self, data):
        tag_objects = []
        errors = []

        for item in data:
            name = item.get('name', '').lower()
            if not name:
                errors.append({'name': ['This field is required.']})
                continue

            obj, _ = Tag.objects.get_or_create(name=name)
            tag_objects.append(obj)

        if errors:
            raise serializers.ValidationError(errors)

        return tag_objects


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        list_serializer_class = TagListSerializer 

class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    media = PostMediaSerializer(many=True, required=False)
    original_post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False)

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        is_public = validated_data.pop('is_public', None)
        
        if isinstance(is_public, str):
            is_public = is_public.lower() == 'true'
        
        post = Post.objects.create(**validated_data, is_public=is_public)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        media_data = validated_data.pop('media', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags:
            instance.tags.set(tags)

        for media in media_data:
            PostMedia.objects.create(post=instance, **media)

        return instance

    def get_media(self, obj):
        return PostMediaSerializer(obj.media.all(), many=True).data  # Serialize media files

    def get_tags(self, obj):
        return [f"#{tag.name}" for tag in obj.tags.all()]  # Format tags as list of strings



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
