from django.urls import path
from .views import (
    UserListCreateView,
    LogoutViewSet,
    PasswordChangeView,
    UserAvatarUploadView,
    UserViewSet,
    SubscriptionsView,
    SubscribeView
)

app_name = 'user_login'

urlpatterns = [
    path('<int:id>/', UserViewSet.as_view({'get': 'retrieve'}),
         name='user-profile'),
    path('', UserListCreateView.as_view(), name="user_auth"),
    path('set_password/', PasswordChangeView.as_view(), name="set_password"),
    path('auth/token/logout/', LogoutViewSet.as_view(), name="logout"),
    path('me/', UserViewSet.as_view({'get': 'me'}), name="me"),
    path('me/avatar/', UserAvatarUploadView.as_view(), name='user-avatar'),
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
    path('<int:id>/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
