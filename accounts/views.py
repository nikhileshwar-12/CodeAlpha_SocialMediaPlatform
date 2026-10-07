from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from posts.models import Post
from posts.utils import annotate_posts

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import Follow, Profile

User = get_user_model()


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def annotate_users(queryset, viewer):
    """Add follower counts and an `is_following` flag (for the current viewer) to a User queryset."""
    queryset = queryset.select_related("profile").annotate(
        followers_total=Count("followers", distinct=True),
        posts_total=Count("posts", distinct=True),
    )
    if viewer.is_authenticated:
        queryset = queryset.annotate(
            is_following=Exists(Follow.objects.filter(follower=viewer, following=OuterRef("pk")))
        )
    return queryset


# ------------------------------------------------------------------- auth views
def register(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Connectly, {user.first_name}! Set up your profile to get started.")
            return redirect("accounts:profile_edit")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out. See you soon!")
        return super().post(request, *args, **kwargs)


# ---------------------------------------------------------------- profile views
def profile(request, username):
    profile_user = get_object_or_404(annotate_users(User.objects.all(), request.user), username=username)
    Profile.objects.get_or_create(user=profile_user)  # safety net for users created without a profile

    posts = annotate_posts(Post.objects.filter(author=profile_user), request.user)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "page_obj": page_obj,
            "posts": page_obj.object_list,
            "following_total": profile_user.following.count(),
            "is_own_profile": request.user == profile_user,
        },
    )


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"form": form, "profile": profile})


@login_required
@require_POST
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        if _is_ajax(request):
            return JsonResponse({"ok": False, "message": "You cannot follow yourself."}, status=400)
        messages.error(request, "You cannot follow yourself.")
        return redirect("accounts:profile", username=username)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if created:
        following = True
    else:
        follow.delete()
        following = False

    if _is_ajax(request):
        return JsonResponse(
            {"ok": True, "following": following, "followers_count": target.followers.count()}
        )
    messages.success(request, f"You are {'now' if following else 'no longer'} following @{target.username}.")
    return redirect(request.POST.get("next") or "accounts:profile", username=username)


def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_ids = Follow.objects.filter(following=profile_user).values_list("follower_id", flat=True)
    users = annotate_users(User.objects.filter(id__in=user_ids), request.user).order_by("username")
    return render(
        request,
        "accounts/follow_list.html",
        {"profile_user": profile_user, "users": users, "title": "Followers"},
    )


def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_ids = Follow.objects.filter(follower=profile_user).values_list("following_id", flat=True)
    users = annotate_users(User.objects.filter(id__in=user_ids), request.user).order_by("username")
    return render(
        request,
        "accounts/follow_list.html",
        {"profile_user": profile_user, "users": users, "title": "Following"},
    )


def user_search(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.none()
    if query:
        users = annotate_users(
            User.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ),
            request.user,
        ).order_by("-followers_total", "username")[:30]
    return render(request, "accounts/search.html", {"query": query, "users": users})
