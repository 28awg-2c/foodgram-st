from django.urls import path
from .views import (
    RecipeView,
    RecipeOneView,
    RecipeShortLinkView,
    DownloadShoppingCartView,
    ShoppingCartView,
    FavoriteView
)

app_name = 'foodgram_app'

urlpatterns = [
    path('', RecipeView.as_view(), name='index'),
    path('<int:id>/', RecipeOneView.as_view(), name='detail'),
    path('<int:id>/get-link/',
         RecipeShortLinkView.as_view({'get': 'get_short_link'}),
         name='short-link'),
    path('download_shopping_cart/',
         DownloadShoppingCartView.as_view(), name='download'),
    path('<int:id>/shopping_cart/', ShoppingCartView.as_view(),
         name='shop_list'),
    path('<int:id>/favorite/', FavoriteView.as_view(), name='favorites_list'),
]
