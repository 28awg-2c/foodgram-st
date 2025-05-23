from rest_framework import generics
from rest_framework.permissions import AllowAny
from foodgram_app.models import Ingredient
from .serializers import IngredientSerializer


class IngredientView(generics.ListAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Отключаем пагинацию согласно документации

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name:
            # Ищем ингредиенты, у которых name начинается с переданной строки (регистронезависимо)
            queryset = queryset.filter(name__istartswith=name)

        return queryset.order_by('name')


class IngredientDetailView(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
