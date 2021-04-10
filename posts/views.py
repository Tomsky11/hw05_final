from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'group.html',
                  {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse('posts:index'))
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_author = author.posts.all()
    paginator = Paginator(posts_author, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/profile.html',
                  {'author': author,
                   'page': page})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts_author = author.posts.all()
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post.html',
                  {'author': author,
                   'posts_author': posts_author,
                   'post': post})


@login_required
def post_edit(request, username, post_id):
    post_kwargs = {'username': username, 'post_id': post_id}
    username = get_object_or_404(User, username=username)
    if request.user == username:
        post = get_object_or_404(Post, author=username, id=post_id)
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect(reverse('posts:post', kwargs=post_kwargs))
        return render(request, 'posts/new.html', {'form': form, 'post': post})
    return redirect(reverse('posts:post', kwargs=post_kwargs))


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)

'''
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author=username, id=post_id)
    form = CommentForm(request.POST or None)
    post_kwargs = {'username': username, 'post_id': post_id}
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.save()
    return redirect(reverse('posts:post', kwargs=post_kwargs))
    return render(request, 'posts/new.html', {'form': form, 'post': post})
'''


def add_comment(request, username, post_id):
    form = PostForm(request.POST or None)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    return render(request, 'posts/post.html', {'form': form, 'post': post})
