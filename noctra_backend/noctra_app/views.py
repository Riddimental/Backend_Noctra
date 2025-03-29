from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    # Get the profile of the authenticated user
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # Serialize the basic profile data
        serializer = UserProfileSerializer(user_profile)
        
        # Add custom data to the response using the new methods
        profile_data = serializer.data
        profile_data['profile_pic_url'] = user_profile.get_profile_pic_url()
        profile_data['cover_pic_url'] = user_profile.get_cover_pic_url()
        profile_data['role_display_name'] = user_profile.get_role_display_name()
        
        return Response(profile_data)
    except UserProfile.DoesNotExist:
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

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Require login for all users

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        profile_data = serializer.data
        profile_data['profile_pic_url'] = instance.get_profile_pic_url()
        profile_data['cover_pic_url'] = instance.get_cover_pic_url()
        profile_data['role_display_name'] = instance.get_role_display_name()
        return Response(profile_data)

    def update(self, request, *args, **kwargs):
        # Call the parent update method for the standard update process
        response = super().update(request, *args, **kwargs)
        # After update, include the custom data in the response
        instance = self.get_object()
        response.data['profile_pic_url'] = instance.get_profile_pic_url()
        response.data['cover_pic_url'] = instance.get_cover_pic_url()
        response.data['role_display_name'] = instance.get_role_display_name()
        return response


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

class ClubAdminViewSet(viewsets.ModelViewSet):
    queryset = ClubAdmin.objects.all()
    serializer_class = ClubAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]  # Only admins can access

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
