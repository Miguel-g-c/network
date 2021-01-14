import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Profile, Post


def index(request):
    return render(request, "network/index.html")

def postbox(request, postbox, username=None):

    # Filter posts returned based on postbox
    if postbox == "allposts":
        posts = Post.objects.all()

    elif postbox == "following":
        if request.user.is_authenticated:
            following = Profile.objects.get(user=request.user).following.all()
            posts = Post.objects.filter(user__in=following)
        else:
            return JsonResponse({"error": "Acces forbidden."}, status=400)

    elif postbox == "profile" and username is not None:
        if request.user.is_authenticated:
            posts = Post.objects.filter(user__username=username)
        else:
            return JsonResponse({"error": "Acces forbidden."}, status=400)

    else:
        return JsonResponse({"error": "Invalid postbox."}, status=400)

    # Return posts in reverse chronologial order
    posts = posts.order_by("-timestamp").all()

    # Using pagination to render 10 posts per page
    posts_paginator = Paginator(posts, 10)

    response = {
        'num_pages': posts_paginator.num_pages,
        'num_posts': posts_paginator.count,
        'data': {}
    }

    for i in posts_paginator.page_range:
        response['data'][i] = [post.serialize() for post in posts_paginator.page(i)]

    for k in response['data']:
        for i in range(len(response['data'][k])):
            response['data'][k][i]['liked_by_user'] = request.user.username in response['data'][k][i]['liking']

    return JsonResponse(response, safe=False)

@csrf_exempt
@login_required
def new_post(request):

    # Posting a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check post
    data = json.loads(request.body)
    post_content = data.get("post")

    if post_content == "":
        return JsonResponse({
            "error": "Empty post not accepted."
        }, status=400)

    elif len(post_content) > 280:
        return JsonResponse({
            "error": "Max post length is 280 characters."
        }, status=400)

    # Create the new post
    post = Post(
        user = request.user,
        post = post_content
    )
    post.save()

    return JsonResponse({"message": "Post created successfully."}, status=201)

@csrf_exempt
@login_required
def post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        response = post.serialize()
        response['liked_by_user'] = request.user.username in response['liking']
        return JsonResponse(response)

    # Update post
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("liked") is not None:
            if data.get("liked"):
                post.likes.add(request.user)
            else:
                post.likes.remove(request.user)
        if data.get("archived") is not None:
            post.archived = data["archived"]
        post.save()
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

@csrf_exempt
@login_required
def profile(request, username):

    # Query for requested post
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    # Return profile contents
    if request.method == "GET":
        response = profile.serialize()
        return JsonResponse(response)

    # Profile must be via GET
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user and profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile = Profile(user = user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
