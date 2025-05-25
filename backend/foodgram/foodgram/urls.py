from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('foodgram_app.urls')),
    path('admin/', admin.site.urls),
    path('api/users/', include('user_login.urls')),
    path('api/auth/', include("djoser.urls")),
    path('api/auth/', include("djoser.urls.authtoken")),
    path('api/recipes/', include('foodgram_app.urls')),
    path('api/ingredients/', include('user_page.urls')),
]
