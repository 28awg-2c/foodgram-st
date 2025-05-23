from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': ("Пользователь с таким никнеймом уже существует."),
        },
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        error_messages={
            'unique': ("Пользователь с таким email уже существует."),
        },
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Уникальное имя
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to...',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Уникальное имя
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user...',
    )
    avatar = models.ImageField(
        upload_to='static/users_avatars/',
        null=True,
        blank=True
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

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
