from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Напишите название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка',
        help_text='Напишите латиницей ссылку'
    )
    description = models.TextField(
        max_length=200,
        verbose_name='Описание',
        help_text='Напишите описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name='Текст',
        help_text='Опишите свои мысли'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Добавьте дату публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Кто автор',
        on_delete=models.CASCADE,
        related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        related_name="groups",
        blank=True,
        null=True,
        help_text='Выберите группу'
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]
