from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator, 'post_list': posts}
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {"group": group, 'posts': posts,
                   'page': page, 'paginator': paginator}
                  )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html',
                  {'author': author, 'page': page,
                   'paginator': paginator, 'count': count, 'posts': posts}
                  )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    return render(request, 'post.html', {'author': author, 'post': post})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    login_user = request.user
    if login_user != post.author:
        return redirect(reverse('post',
                                kwargs={
                                    'username': post.author.username,
                                    'post_id': post_id,
                                }
                                )
                        )
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect(reverse('post',
                                kwargs={
                                    'username': post.author.username,
                                    'post_id': post_id,
                                }
                                ))
    return render(request, 'edit_post.html', {'form': form, 'post': post})
