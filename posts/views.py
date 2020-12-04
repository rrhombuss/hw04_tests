from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator, 'post_list': post_list}
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
    if not request.user.is_authenticated:
        return redirect('/auth/login')
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
# прочитал на stackoverflow насколько я понял должно работать, но не работает
# User.objects.filter(username=username)
# author.objects.all() #
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


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    login_user = request.user
    if not login_user.is_authenticated:
        return redirect('/auth/login')
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
