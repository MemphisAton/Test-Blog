from django.contrib.postgres.search import TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.db.models.functions import Greatest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from taggit.models import Tag

from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post


def post_list(request, tag_slug=None):
    post_l = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_l = post_l.filter(tags__in=[tag])

    paginator = Paginator(post_l, 3)  # Постраничная разбивка с 3 постами на страницу
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)  # Если page_number не целое число, то выдать первую страницу
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # Если page_number находится вне диапазона, то последнюю страницу
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts, 'tag': tag})


# class PostListView(ListView):
#     """
#     Альтернативное представление списка постов
#     """
#     queryset = Post.published.all()  # конкретно-прикладной набор запросов QuerySet
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    '''
    Указанная функция извлекает объект, соответствующий переданным параметрам,
    либо исключение HTTP с кодом состояния 404
    '''
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)  # Список активных комментариев к этому посту
    form = CommentForm()  # Форма для комментирования пользователями

    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'form': form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'memphisaton@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None  # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():  # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)  # Назначить пост комментарию
        comment.post = post  # Сохранить комментарий в базе данных
        comment.save()
    return render(request,
                  'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    # if form.is_valid():
    #     query = form.cleaned_data['query']
    #     search_vector = SearchVector('title', weight='B') + SearchVector('body', weight='A')
    #     search_query = SearchQuery(query)
    #     results = Post.published.annotate(
    #         search=search_vector,
    #         rank=SearchRank(search_vector, search_query)
    #     ).filter(rank__gte=0.2).order_by('-rank')
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = (Post.published.annotate(
            # аннотируют каждую запись двумя значениями сходства: одно для title, другое для содержимого body
            title_similarity=TrigramSimilarity('title', query),
            body_similarity=TrigramSimilarity('body', query))
                   .annotate(similarity=Greatest('title_similarity', 'body_similarity'))
                   .filter(similarity__gt=0.1)
                   .order_by('-similarity'))
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
