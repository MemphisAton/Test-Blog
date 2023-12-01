from django.contrib import admin

from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    '''
    Мы сообщаем сайту администрирования, что модель зарегистрирована на сайте с использованием
    конкретно-прикладного класса, который наследует от ModelAdmin.
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/.
    '''
    list_display = ['title', 'slug', 'author', 'publish', 'status']  # какие поля показывать
    list_filter = ['status', 'created', 'publish', 'author']  # по каким полям фильтровать
    search_fields = ['title', 'body']  # по каким полям вести поиск
    prepopulated_fields = {'slug': ('title',)}  # автоматическое заполнения поля slug по title
    raw_id_fields = ['author']  # отображается поисковым виджетом
    date_hierarchy = 'publish'  # навигационные ссылки для навигации по иерархии дат
    ordering = ['status', 'publish']  # порядок отображения


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
