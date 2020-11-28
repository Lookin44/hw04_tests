from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
import datetime as dt
from .forms import PostForm
from .models import Group, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator,
               }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all()
    paginator = Paginator(group_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group,
               'page': page,
               'paginator': paginator,
               }
    return render(request, 'group.html', context)


def year(request):
    return {'year': dt.datetime.now().year}


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    posts_count = post_list.count()
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator,
               'posts_count': posts_count,
               'profile': profile,
               }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    post_list = Post.objects.filter(author=profile).all()
    posts_count = post_list.count()
    context = {
        'profile': profile,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'post.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'post_new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = user.posts.get(id=post_id)
    if request.user != user:
        return redirect('post', username=user.username, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('post',
                        username=request.user.username,
                        post_id=post_id
                        )
    return render(request, 'post_new.html', {'form': form, 'post': post})
