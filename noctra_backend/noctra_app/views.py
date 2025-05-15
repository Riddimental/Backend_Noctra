import json
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, identifier=None):
    # Case: /me/ or authenticated user
    if identifier is None or str(identifier) == str(request.user.id) or str(identifier) == request.user.username:
        try:
            user_profile = UserProfile.objects.get(user=request.user)

            if request.method == 'GET':
                serializer = UserProfileSerializer(user_profile)
                profile_data = serializer.data
                profile_data['profile_pic_url'] = user_profile.get_profile_pic_url()
                profile_data['cover_pic_url'] = user_profile.get_cover_pic_url()
                profile_data['user_type_display_name'] = user_profile.get_user_type_display_name()
                profile_data['system_role_display_name'] = user_profile.get_system_role_display_name()
                return Response(profile_data)

            elif request.method == 'PATCH':
                serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

    # Case: identifier is either a user ID or username of another user
    user_profile = None

    # Try to fetch by numeric user ID first
    if str(identifier).isdigit():
        user = User.objects.filter(id=identifier).first()
        if user:
            user_profile = UserProfile.objects.filter(user=user).first()


    # If not found by ID, try username
    if not user_profile:
        user_profile = UserProfile.objects.filter(user__username=identifier).first()

    if user_profile:
        if request.method == 'GET':
            serializer = UserProfileSerializer(user_profile)
            profile_data = serializer.data
            profile_data['profile_pic_url'] = user_profile.get_profile_pic_url()
            profile_data['cover_pic_url'] = user_profile.get_cover_pic_url()
            profile_data['user_type_display_name'] = user_profile.get_user_type_display_name()
            profile_data['system_role_display_name'] = user_profile.get_system_role_display_name()
            basic_data = {
                'id': user_profile.id,
                'username': user_profile.username,
                'user_type': user_profile.user_type,
                'profile_pic_url': user_profile.get_profile_pic_url(),
                }
            return Response(basic_data)
    else:
        return Response({"error": "Profile not found"}, status=404)



@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_club(request):
    serializer = ClubSerializer(data=request.data)
    if serializer.is_valid():
        club = serializer.save(created_by=request.user)
        club.admins.add(request.user)
        return Response(ClubSerializer(club).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ClubProfileViewSet(viewsets.ModelViewSet):
    queryset = ClubProfile.objects.all()
    serializer_class = ClubProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        is_public = self.request.data.get('is_public', True)
        original_post_data = self.request.data.get('original_post', None)

        # Ensure original_post is passed as primary key or ID
        original_post = None
        if original_post_data:
            try:
                original_post = Post.objects.get(id=original_post_data)
            except Post.DoesNotExist:
                raise serializers.ValidationError({"original_post": "Invalid original post ID."})

        post = serializer.save(owner=self.request.user, is_public=is_public, original_post=original_post)

        # Handle tags if provided
        self.handle_tags(post)

        # Optionally handle media upload separately if needed
        self.handle_media_upload(post)
        
    def get_queryset(self):
        user_id = self.kwargs.get('user_id', None)
        if user_id:
            return Post.objects.filter(owner_id=user_id).order_by('-created_at')
        return Post.objects.filter(owner=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>\d+)')
    def user_posts(self, request, user_id=None):
        # This action will be used for fetching posts of a specific user
        posts = Post.objects.filter(owner_id=user_id).order_by('-created_at')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        post = serializer.save()

        # Handle tags if provided
        self.handle_tags(post)

        # Optionally handle media upload separately if needed
        self.handle_media_upload(post)

    def handle_tags(self, post):
        # Ensure tags are passed as a stringified JSON in FormData
        tags_data = self.request.data.get('tags', None)

        if tags_data:
            try:
                tags = json.loads(tags_data)  # Convert the string to a list of dictionaries
                for tag_data in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_data['name'])
                    post.tags.add(tag)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"tags": "Invalid tags format."})

    def handle_media_upload(self, post):
        # Handle media files from FormData
        media_files = self.request.FILES.getlist('media')
        if media_files:
            for media in media_files:
                file_type = self.get_file_type(media.name)
                PostMedia.objects.create(post=post, file=media, file_type=file_type)

    def get_file_type(self, filename):
        ext = filename.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif ext in ['mp4', 'mov', 'avi']:
            return 'video'
        elif ext in ['mp3', 'wav']:
            return 'audio'
        else:
            return 'other'

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
