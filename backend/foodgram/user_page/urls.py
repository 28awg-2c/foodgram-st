from django.urls import path
from .views import IngredientView, IngredientDetailView

app_name = 'user_page'

urlpatterns = [
    path('<int:pk>/', IngredientDetailView.as_view(), name='IngredientView'),
    path('', IngredientView.as_view(), name='IngredientView'),

]
