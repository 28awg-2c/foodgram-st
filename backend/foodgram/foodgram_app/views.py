from rest_framework import generics, status, permissions, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Recipe
from user_page.models import Shoping, Favorite
from .serializers import RecipeListSerializer, RecipeCreateSerializer, RecipeShortSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.conf import settings
from rest_framework.views import APIView
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

class RecipeOneView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_url_kwarg = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return RecipeCreateSerializer
        return RecipeListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('author')

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(
            queryset, id=self.kwargs.get(self.lookup_url_kwarg))
        self.check_object_permissions(self.request, obj)
        return obj

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PATCH', 'DELETE'] and obj.author != request.user:
            self.permission_denied(
                request,
                message="Вы не являетесь автором этого рецепта",
                code=status.HTTP_403_FORBIDDEN
            )

    def update(self, request, *args, **kwargs):
        recipe_instance = self.get_object()
        self.validate_object_permissions(request, recipe_instance)

        update_serializer = self.get_serializer(
            instance=recipe_instance,
            data=request.data,
            partial=kwargs.get('partial', False)
        )

        update_serializer.is_valid(raise_exception=True)
        self.perform_update(update_serializer)

        response_serializer = RecipeListSerializer(
            instance=recipe_instance,
            context=self.get_serializer_context()
        )

        return self.build_response(
            data=response_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "У вас нет прав для удаления этого рецепта"},
                status=status.HTTP_403_FORBIDDEN
            )

    def validate_object_permissions(self, request, obj):
        self.check_object_permissions(request, obj)

    def validate_data(self, serializer, raise_error=True):
        if not serializer.is_valid() and raise_error:
            raise serializers.ValidationError(serializer.errors)

    def execute_update(self, serializer):
        self.perform_update(serializer)

    def build_response(self, data, status_code):
        return Response(data=data, status=status_code)


class RecipeShortLinkView(viewsets.ViewSet):
    """
    Отдельный ViewSet для работы с короткими ссылками на рецепты
    """
    queryset = Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]  # Или другие permissions по необходимости

    @action(detail=True, methods=['get'], url_path='short-link')
    def get_short_link(self, request, id=None):
        """
        Получение короткой ссылки на рецепт
        ---
        parameters:
            - name: id
              required: true
              type: string
              paramType: path
              description: ID рецепта
        """
        try:
            recipe = self.queryset.get(id=id)
            short_link = f"{settings.BASE_URL}/api/recipes/{recipe.id}"
            
            return Response(
                {"short-link": short_link},
                status=status.HTTP_200_OK
            )
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден"},
                status=status.HTTP_404_NOT_FOUND
            )


class CustomPagination(PageNumberPagination):
    page_size = 6  # Дефолтное количество элементов на странице
    page_size_query_param = 'limit'  # Параметр для изменения количества
    max_page_size = 100 

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class RecipeView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all().order_by('-id')
    #queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeCreateSerializer
        # else:
        return RecipeListSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author')
        params = self.request.GET

        if 'author' in params:
            queryset = queryset.filter(author_id=params['author'])

        if 'is_favorited' in params and params['is_favorited'] == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(in_favorites__user=self.request.user)
                print(queryset)

        if 'is_in_shopping_cart' in params and params['is_in_shopping_cart'] == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    shopping_carts__user=self.request.user)

        return queryset

    def list(self, request, *args, **kwargs):
        # Обработка параметра limit
        if limit := request.query_params.get('limit'):
            try:
                self.pagination_class.page_size = int(limit)
            except (TypeError, ValueError):
                pass

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        response_serializer = RecipeListSerializer(
            recipe,
            context={'request': request}
        )

        if self.request.method == "POST":
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'results': [response_serializer.data]},
                status=status.HTTP_201_CREATED
            )


class ShoppingCartView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    Добавление рецепта в список покупок
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeShortSerializer
    lookup_url_kwarg = 'id'

    def create(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        
        # Проверяем существование рецепта
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Проверяем, не добавлен ли уже рецепт
        if Shoping.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем запись в списке покупок
        shopping_item = Shoping.objects.create(user=user, recipe=recipe)
        
        # Сериализуем рецепт для ответа
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        
        # Проверяем существование рецепта
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Пытаемся найти запись в списке покупок
        shopping_item = Shoping.objects.filter(user=user, recipe=recipe).first()
        
        if not shopping_item:
            return Response(
                {'detail': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Удаляем запись
        shopping_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    Добавление рецепта в избранное
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeShortSerializer
    lookup_url_kwarg = 'id'

    def create(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        
        # Проверяем существование рецепта
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Проверяем, не добавлен ли уже рецепт в избранное
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже есть в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем запись в избранном
        Favorite.objects.create(user=user, recipe=recipe)
        
        # Сериализуем рецепт для ответа
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Удаление рецепта из избранного"""
        user = request.user
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        
        # Проверяем существование рецепта
        recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Пытаемся найти запись в избранном
        favorite = Favorite.objects.filter(user=user, recipe=recipe).first()
        
        if not favorite:
            return Response(
                {'detail': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Удаляем запись
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        # Получаем все рецепты в списке покупок пользователя
        shopping_items = Shoping.objects.filter(user=request.user).select_related('recipe')
        
        if not shopping_items.exists():
            return Response(
                {'detail': 'Ваш список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Собираем все ингредиенты с количеством
        ingredients = {}
        for item in shopping_items:
            recipe = item.recipe
            for ingredient in recipe.recipe_ingredient.all():
                key = (ingredient.ingredient.name, 
                       ingredient.ingredient.measurement_unit)
                if key in ingredients:
                    ingredients[key] += ingredient.amount
                else:
                    ingredients[key] = ingredient.amount
        
        # Определяем формат из параметра запроса (по умолчанию PDF)
        file_format = request.query_params.get('format', 'pdf').lower()
        
        if file_format == 'txt':
            return self._generate_txt_file(ingredients)
        elif file_format == 'csv':
            return self._generate_csv_file(ingredients)
        else:
            return self._generate_pdf_file(ingredients)
    
    def _generate_pdf_file(self, ingredients):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # Заголовок документа
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Список покупок")
        p.setFont("Helvetica", 12)
        
        y_position = 750
        for (name, unit), amount in ingredients.items():
            p.drawString(100, y_position, f"- {name}: {amount} {unit}")
            y_position -= 20
            if y_position < 50:
                p.showPage()
                y_position = 750
        
        p.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        return response
    
    def _generate_txt_file(self, ingredients):
        content = "Список покупок:\n\n"
        for (name, unit), amount in ingredients.items():
            content += f"- {name}: {amount} {unit}\n"
        
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
    
    def _generate_csv_file(self, ingredients):
        content = "Ингредиент,Количество,Единица измерения\n"
        for (name, unit), amount in ingredients.items():
            content += f"{name},{amount},{unit}\n"
        
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.csv"'
        return response