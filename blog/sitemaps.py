from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    '''
    определил конкретно-прикладную карту сайта, унаследовав класс Sitemap модуля sitemaps.
    '''
    changefreq = 'weekly'  # частота изменения страниц постов
    priority = 0.9  # релевантность страниц постов на веб-сайте

    def items(self):
        '''
        возвращает набор запросов QuerySet объектов, подлежащих включению в эту карту сайта.
        '''
        return Post.published.all()

    def lastmod(self, obj):
        '''
        получает каждый возвращаемый методом items() объект и возвращает время последнего изменения объекта
        '''
        return obj.update
