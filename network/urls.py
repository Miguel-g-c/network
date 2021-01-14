
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posting", views.new_post, name="posting"),
    path("post/<int:post_id>", views.post, name="post"),
    path("posts/<str:postbox>", views.postbox, name="postbox"),
    path("posts/<str:postbox>/<str:username>", views.postbox, name="postbox"),
    path("profile/<str:username>", views.profile, name="profile"),
]
