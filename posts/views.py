from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Follow

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post
from .utils import annotate_posts

User = get_user_model()


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _suggested_users(user, limit=5):
    """People the user doesn't follow yet, most-followed first."""
    if not user.is_authenticated:
        return User.objects.none()
    following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)
    return (
        User.objects.exclude(id=user.id)
        .exclude(id__in=following_ids)
        .select_related("profile")
        .annotate(followers_total=Count("followers", distinct=True))
        .order_by("-followers_total", "username")[:limit]
    )


def _render_timeline(request, posts, template, extra=None):
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "post_form": PostForm(),
        "suggested_users": _suggested_users(request.user),
    }
    if extra:
        context.update(extra)
    return render(request, template, context)


# --------------------------------------------------------------------- timeline
def feed(request):
    """Home: posts from people you follow (+ your own). Anonymous users see Explore."""
    if not request.user.is_authenticated:
        return redirect("posts:explore")
    following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
    posts = annotate_posts(Post.objects.filter(Q(author__in=following_ids) | Q(author=request.user)), request.user)
    return _render_timeline(request, posts, "posts/feed.html", {"following_count": len(following_ids)})


def explore(request):
    """All posts from everyone, newest first (public)."""
    posts = annotate_posts(Post.objects.all(), request.user)
    return _render_timeline(request, posts, "posts/explore.html")


# ------------------------------------------------------------------------ posts
@login_required
@require_POST
def post_create(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post has been published.")
    else:
        for error in form.errors.values():
            messages.error(request, error[0])
    return redirect(request.POST.get("next") or "posts:feed")


def post_detail(request, pk):
    post = get_object_or_404(annotate_posts(Post.objects.all(), request.user), pk=pk)
    comments = post.comments.select_related("author", "author__profile")
    return render(
        request,
        "posts/post_detail.html",
        {"post": post, "comments": comments, "comment_form": CommentForm()},
    )


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You can only delete your own posts.")
    post.delete()
    messages.info(request, "Post deleted.")
    return redirect(request.POST.get("next") or "posts:feed")


# -------------------------------------------------------------- likes/comments
@login_required
@require_POST
def like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    liked = created
    if _is_ajax(request):
        return JsonResponse({"ok": True, "liked": liked, "like_count": post.likes.count()})
    return redirect(request.POST.get("next") or post.get_absolute_url())


@login_required
@require_POST
def comment_add(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Comment cannot be empty.")
    return redirect(post.get_absolute_url())


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("post"), pk=pk)
    if request.user not in (comment.author, comment.post.author) and not request.user.is_staff:
        return HttpResponseForbidden("You cannot delete this comment.")
    post_url = comment.post.get_absolute_url()
    comment.delete()
    messages.info(request, "Comment deleted.")
    return redirect(post_url)
