from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Group, Post, Follow

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
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse('posts:index'))
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    following = False
    author = get_object_or_404(User, username=username)
    posts_author = author.posts.all()
    paginator = Paginator(posts_author, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    return render(request, 'posts/profile.html',
                  {'author': author,
                   'following': following,
                   'page': page})


def post_view(request, username, post_id):
    form = CommentForm()
    author = get_object_or_404(User, username=username)
    posts_author = author.posts.all()
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'posts/post.html',
                  {'author': author,
                   'posts_author': posts_author,
                   'post': post,
                   'comments': comments,
                   'form': form}
    )


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


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    post_kwargs = {'username': username, 'post_id': post_id}
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect(reverse('posts:post', kwargs=post_kwargs))


@login_required
def follow_index(request):
    latest = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user,
                                     author=author)
    return redirect(reverse('posts:profile', kwargs={'username': author}))


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect(reverse('posts:profile', kwargs={'username': author}))
