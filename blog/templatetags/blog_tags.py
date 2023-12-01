import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from ..models import Post

register = template.Library()  # используется для регистрации шаблонных тегов и фильтров приложения


@register.simple_tag  # зарегистрируем как простой тег, можно поменять имя (name='my_tag')
def total_posts():  # создали простой шаблонный тег, который возвращает число опубликованных в блоге постов
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):  # выводит список последних добавленный постов
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]


@register.filter(name='markdown')  # имя в шаблоне
def markdown_format(text):
    return mark_safe(markdown.markdown(text))