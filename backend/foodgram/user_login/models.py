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
        unique=True,
        error_messages={
            'unique': ("Пользователь с таким email уже существует."),
        },
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'
