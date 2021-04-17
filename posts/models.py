from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст публикации',
                            help_text='Введите текст публикации')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, verbose_name='Автор публикации',
                               on_delete=models.CASCADE, related_name='posts')
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Сообщество',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Картинка'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Сообщество', max_length=200, unique=True)
    slug = models.SlugField('slug', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание',
                                   null=True, blank=True)

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите комментарий'
    )
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комеентарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_object'
        )]
