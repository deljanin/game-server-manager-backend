from django.urls import path, include
from api.views import CreateUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from api.views import GameServerViewSet
from django.conf import settings


router = DefaultRouter()
router.register(r'api/game-server', GameServerViewSet, basename='gameserver')

urlpatterns = [
    
    path('api/user/login/', TokenObtainPairView.as_view(),name='get_token'),
    path('api/token/refresh', TokenRefreshView.as_view(),name='refresh_token'),
    path('api/auth/', include("rest_framework.urls")),

    path('', include(router.urls)),
]

if settings.USER_REGISTRATION_ENABLED:
    urlpatterns.append(path("api/register/", CreateUserView.as_view()))