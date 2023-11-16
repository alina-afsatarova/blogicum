from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post

User = get_user_model()

# все посты
All_POSTS = Post.objects.select_related(
    'location', 'category'
)

# опубликованные посты с опубликованной категорией,
# дата публикации поста — не позже текущего времени
FILTERED_POSTS = All_POSTS.filter(
    is_published=True,
    category__is_published=True,
    pub_date__lte=timezone.now()
)


def get_comment_count(post):
    """Получает количество комментариев к посту."""
    return post.annotate(comment_count=Count('comments'))


class ProfileDetailView(DetailView):
    """Страница пользователя."""

    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user == self.object:
            posts = get_comment_count(All_POSTS).filter(
                author=self.object
            ).order_by('-pub_date')
        else:
            posts = get_comment_count(FILTERED_POSTS).filter(
                author=self.object
            ).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ProfileURLMixin:
    """Создает ссылку на профиль."""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostURLMixin:
    """Создает ссылку на страницу поста."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class ProfileUpdateView(LoginRequiredMixin, ProfileURLMixin, UpdateView):
    """Редактирование профиля."""

    template_name = 'blog/user.html'
    model = User
    form_class = UserForm

    def get_object(self):
        return self.request.user


class PostCreateView(LoginRequiredMixin, ProfileURLMixin, CreateView):
    """Создание новой публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostMixin(LoginRequiredMixin):

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect(
                'blog:post_detail',
                kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, PostURLMixin, UpdateView):
    """Редактирование публикации."""

    form_class = PostForm


class PostDeleteView(PostMixin, ProfileURLMixin, DeleteView):
    """Удаление публикации."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostDetailView(DetailView):
    """Страница публикации."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(
                FILTERED_POSTS,
                pk=self.kwargs['post_id']
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostListView(ListView):
    """Главная страница."""

    model = Post
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'

    queryset = get_comment_count(FILTERED_POSTS)


def category_posts(request, category_slug):
    """Страница категории."""
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = get_comment_count(
        category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


class CommentCreateView(LoginRequiredMixin, PostURLMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentMixin(LoginRequiredMixin, PostURLMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if instance.author != request.user:
            return redirect(
                'blog:post_detail',
                kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария."""

    pass
