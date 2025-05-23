from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserListCreateView,
    LogoutViewSet,
    PasswordChangeView,
    UserAvatarUploadView,
    UserViewSet,
    SubscriptionsView,
    SubscribeView
)

# router = DefaultRouter()
# Изменили basename и префикс
# router.register(r'', UserAuthViewSet, basename='users')

app_name = 'user_login'

urlpatterns = [
    # path('', include(router.urls)),
    path('<int:id>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-profile'),
    path('', UserListCreateView.as_view(), name="user_auth"),
    path('set_password/', PasswordChangeView.as_view(), name="set_password"),
    path('auth/token/logout/', LogoutViewSet.as_view(), name="logout"),
    path('me/', UserViewSet.as_view({'get': 'me'}), name="me"),
    #path('', UserViewSet.as_view({'get': 'list'}), name="me"),
    path('me/avatar/', UserAvatarUploadView.as_view(), name='user-avatar'),
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
    path('<int:id>/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
