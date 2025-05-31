import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import User, Follow
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework import generics
from .serializers import (
    UserReadSerializer,
    UserRegistrationSerializer,
    UserWithRecipesSerializer,
    SubscribeSerializer
)


class UserPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100


class UserViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, id, *args, **kwargs):
        try:
            user = get_object_or_404(User, id=id)

            context = {'request': request}

            serializer = UserReadSerializer(user, context=context)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Пользователь не авторизован")
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    pagination_class = UserPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegistrationSerializer
        return UserReadSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return super().get_permissions()


class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]


class LogoutViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            auth_logout(request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"detail":
                 "Both 'current_password' and 'new_password' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"new_password": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.check_password(new_password):
            return Response(
                {"new_password": [
                    "New password must be different from current password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        avatar_data = request.data.get('avatar')

        if not avatar_data:
            return Response(
                {"avatar": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1]

            filename = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)

            user = request.user
            if user.avatar:
                user.avatar.delete(save=False)

            user.avatar.save(filename, data, save=True)

            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)

        except (ValueError, TypeError, AttributeError):
            return Response(
                {"avatar": ["Invalid base64 format."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Аватар не найден."},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubscribeView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        user = request.user

        if user.id == author_id:
            raise ValidationError(
                {'detail': 'Нельзя подписаться на самого себя'},
                code=status.HTTP_400_BAD_REQUEST
            )

        author = get_object_or_404(User, id=author_id)

        if user.follower.filter(author=author):
            raise ValidationError(
                {'detail': 'Вы уже подписаны на этого пользователя'},
                code=status.HTTP_400_BAD_REQUEST
            )

        Follow.objects.create(follower=user, author=author)
        serializer = self.get_serializer(author, context={
            'request': request,
            'recipes_limit': request.query_params.get('recipes_limit')
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, id):
        user = request.user

        author = get_object_or_404(User, id=id)

        follow = user.follower.filter(author=author)
        if not follow:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        }


class SubscriptionsView(generics.ListAPIView):
    serializer_class = UserWithRecipesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SubscriptionsPagination

    def get_queryset(self):
        subscribed_users = self.request.user.follower.all()
        recipes_limit = self.request.query_params.get('recipes_limit')

        queryset = User.objects.filter(
            id__in=subscribed_users.values_list('author', flat=True)
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return Response(self.get_paginated_response(serializer.data))
