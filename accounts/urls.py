from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("search/", views.user_search, name="search"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("u/<str:username>/followers/", views.followers_list, name="followers"),
    path("u/<str:username>/following/", views.following_list, name="following"),
]
