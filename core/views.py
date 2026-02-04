from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Project, StarProject, ConnectionsCount
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.db.models import Q


@login_required(login_url="signin")
def index(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect("settings")

    projects = Project.objects.all().order_by("-created_at")

    project_usernames = [p.user for p in projects]
    profiles = Profile.objects.filter(user__username__in=project_usernames)
    profile_img_map = {p.user.username: p.profileimg.url for p in profiles}

    for project in projects:
        project.profile_img_url = profile_img_map.get(
            project.user, "/media/blank-profile-picture.png"
        )

    context = {
        "user_profile": user_profile,
        "posts": projects,
    }
    return render(request, "index.html", context)


@login_required(login_url="signin")
def search(request):

    if hasattr(request.user, "profile"):
        user_profile = request.user.profile
    else:
        user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        query = request.POST.get("username")
        user_results = Profile.objects.filter(user__username__icontains=query)
        project_results = Project.objects.filter(
            Q(title__icontains=query) | Q(tags__icontains=query)
        )

        context = {
            "user_profile": user_profile,
            "query": query,
            "user_results": user_results,
            "project_results": project_results,
        }
        return render(request, "search.html", context)

    return redirect("/")


@login_required(login_url="signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        user_profile.bio = request.POST["bio"]
        user_profile.location = request.POST["location"]
        user_profile.skills = request.POST["skills"]  # nexus fields
        user_profile.github_url = request.POST["github_url"]  # nexus fields

        if "image" in request.FILES:
            user_profile.profileimg = request.FILES["image"]

        user_profile.save()
        return redirect("profile", pk=request.user.username)

    return render(request, "setting.html", {"user_profile": user_profile})


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password == password2:
            if not email or User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists or Email is left empty")
                return redirect("signup")

            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                user.save()
                # log user in and redirect to settings page.

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id
                )
                new_profile.save()
                return redirect("settings")
        else:
            messages.info(request, "Passwords do not match")
            return redirect("signup")
    else:
        return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("signin")
    else:
        return render(request, "signin.html")


@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    return redirect("signin")


@login_required(login_url="signin")
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_projects = Project.objects.filter(user=pk).order_by("-created_at")

    network_count = ConnectionsCount.objects.filter(
        connection=pk
    ).count()  # how many users have connected to this user (followers)
    connections_count = ConnectionsCount.objects.filter(
        username=pk
    ).count()  # how many users is this user connected to (following)

    is_connected = ConnectionsCount.objects.filter(
        username=request.user.username, connection=pk
    ).exists()

    skills_list = []
    if user_profile.skills:
        skills_list = [skill.strip() for skill in user_profile.skills.split(",")]

    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_projects": user_projects,
        "projects_count": user_projects.count(),
        "is_connected": is_connected,
        "network_count": network_count,  # Network: People following them
        "connections_count": connections_count,  # People they follow
        "skills_list": skills_list,
        "github_url": user_profile.github_url,
    }
    return render(request, "profile.html", context)


@login_required(login_url="signin")
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get("image_upload")
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags = request.POST.get("tags")
        github_link = request.POST.get("github_link")

        new_project = Project.objects.create(
            user=user,
            image=image,
            title=title,
            description=description,
            tags=tags,
            github_link=github_link,
        )

        new_project.save()
        return redirect("/")

    return redirect("/")


@login_required(login_url="signin")
def star_project(request):
    username = request.user.username
    project_id = request.GET.get("project_id")

    project = Project.objects.get(id=project_id)

    star_filter = StarProject.objects.filter(
        project_id=project_id, username=username
    ).first()

    if star_filter is None:
        new_star = StarProject.objects.create(project_id=project_id, username=username)
        new_star.save()
        project.no_of_stars += 1
        project.save()
        return redirect("/")
    else:
        star_filter.delete()
        project.no_of_stars -= 1
        project.save()
        return redirect("/")


@login_required(login_url="signin")
def connect(request):
    if request.method == "POST":
        username = request.user.username  # The user requesting the connection
        connection = request.POST.get("user")  # The user being connected to

        if not connection:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if ConnectionsCount.objects.filter(
            username=username, connection=connection
        ).first():
            delete_connection = ConnectionsCount.objects.get(
                username=username, connection=connection
            )
            delete_connection.delete()
            return redirect(request.META.get("HTTP_REFERER", "/"))
        else:
            new_connection = ConnectionsCount.objects.create(
                username=username, connection=connection
            )
            new_connection.save()
            return redirect(request.META.get("HTTP_REFERER", "/"))

    else:
        return redirect("/")
