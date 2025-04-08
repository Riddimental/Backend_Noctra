from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'clubprofiles', ClubProfileViewSet)
router.register(r'clubadmins', ClubAdminViewSet)
router.register(r'events', EventViewSet)
router.register(r'feeds', FeedViewSet)
router.register(r'posts', PostViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', register, name='register'),
    path('api/userprofiles/me/', get_user_profile, name='get_user_profile'),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
