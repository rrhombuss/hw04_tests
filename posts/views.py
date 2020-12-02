from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator}
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    post_list = group.posts.all()
    paginator = Paginator(post_list, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {"group": group, 'posts': post_list,
                   'page': page, 'paginator': paginator}
                  )


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
    posts = Post.objects.filter(author=author)
    count = posts.count()
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html',
                  {'author': author, 'page': page,
                   'paginator': paginator, 'count': count}
                  )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    return render(request, 'post.html', {'author': author, 'post': post})


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
