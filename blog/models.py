from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    '''
    определяем конкретно-прикладной модельный менеджер. вместо objects
    '''

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        '''
        Доступными вариантами статуса поста являются
        DRAFT и PUBLISHED. Их соответствующими значениями выступают DF и PB, а их
        метками или читаемыми именами являются Draft и Published.
        Post.Status.choices - получить имеющиеся варианты
        Post.Status.labels - получить удобочитаемые имена к меткам статуса
        Post.Status.values - получить фактические значения вариантов к значениям статуса
        Post.Status.names - получить имена
        '''
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,
                            unique_for_date='publish')  # поле slug должно быть уникальным для даты, publish.
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')  # без related_name будет post_set
    body = models.TextField()
    publish = models.DateTimeField(
        default=timezone.now)  # Метод timezone.now возвращает текущую дату/время в формате, зависящем от часового пояса.
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    objects = models.Manager()  # менеджер, применяемый по умолчанию
    published = PublishedManager()  # конкретно-прикладной менеджер
    tags = TaggableManager()

    class Meta:  # класс определяет метаданные модели
        ordering = ['-publish']  # ordering - сортировать результаты по полю publish. Убывающий порядок: -publish.
        indexes = [models.Index(fields=['-publish']), ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')  # без related_name будет comment_set
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created']), ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
