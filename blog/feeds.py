import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list')  # reverse_lazy позволяет использовать обратный URL-адрес до того, как конфигурация URL-адреса проекта будет загружена.
    description = 'New posts of my blog.'

    def items(self):
        '''
        извлекает включаемые в новостную ленту объекты
        '''
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish
