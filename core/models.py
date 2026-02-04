from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True, max_length=250)
    profileimg = models.ImageField(
        upload_to="profile_images", default="blank-profile-picture.png"
    )
    location = models.CharField(max_length=100, blank=True)
    skills = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated skills (e.g. Python, Django)",
    )
    github_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to="post_images")
    description = models.TextField()  # serves as the "Project Description"
    created_at = models.DateTimeField(default=datetime.now)
    no_of_stars = models.IntegerField(default=0)
    title = models.CharField(max_length=200, default="Untitled Project")
    tags = models.CharField(max_length=200, blank=True)
    github_link = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.user


class StarProject(models.Model):
    project_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class ConnectionsCount(models.Model):
    # Conceptually: "Connections"
    username = models.CharField(max_length=100)  # The user who is connecting
    connection = models.CharField(max_length=100)  # The user being connected to

    def __str__(self):
        return self.username
