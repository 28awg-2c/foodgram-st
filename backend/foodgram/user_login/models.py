from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH_TEXT = 150
MAX_LENGTH_PASSWORD = 128
MAX_LENGTH_EMAIL = 254


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        unique=True,
        error_messages={
            'unique': ("Пользователь с таким никнеймом уже существует."),
        },
        verbose_name='Никнейм',
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        error_messages={
            'unique': ("Пользователь с таким email уже существует."),
        },
        verbose_name='Почта',
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='Группы',
        help_text='The groups this user belongs to...',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='Права пользователей',
        help_text='Specific permissions for this user...',
    )
    avatar = models.ImageField(
        upload_to='static/users_avatars/',
        null=True,
        blank=True,
        verbose_name='Фото'
    )

    first_name = models.CharField(max_length=MAX_LENGTH_TEXT)
    last_name = models.CharField(max_length=MAX_LENGTH_TEXT)
    password = models.CharField(max_length=MAX_LENGTH_PASSWORD)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('author')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.author}'
