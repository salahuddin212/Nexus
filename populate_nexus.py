import os
import django
import random

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Nexus.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Project
from faker import Faker

fake = Faker()

# Tech stacks for realism
STACKS = [
    "Python, Django, AWS",
    "React, Node.js, MongoDB",
    "Vue, Firebase",
    "Rust, WebAssembly",
    "Go, Kubernetes, Docker",
    "Swift, iOS",
    "Java, Spring Boot",
    "Meow",
]

TITLES = [
    "AI Chatbot for Customer Service",
    "E-commerce Dashboard",
    "Crypto Trading Bot",
    "Open Source VS Code Extension",
    "Turkish-English Translation API",
    "Smart Home IoT Hub",
]


def create_users(n=10):
    print(f"Creating {n} users...")
    for i in range(n):
        # 1. Create User
        username = fake.user_name()
        if User.objects.filter(username=username).exists():
            continue

        user = User.objects.create_user(
            username=username, email=fake.email(), password="password123"
        )

        # 2. Get Profile (Signal creates it, we just update it)
        try:
            profile = Profile.objects.get(user=user)
            profile.bio = fake.text(max_nb_chars=100)
            profile.location = fake.city()
            profile.skills = random.choice(STACKS)
            profile.github_url = f"https://github.com/{username}"
            profile.save()
        except Profile.DoesNotExist:
            profile = Profile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=100),
                location=fake.city(),
                skills=random.choice(STACKS),
                github_url=f"https://github.com/{username}",
                id_user=user.id,
            )

        # 3. Create a Project for this user (50% chance)
        if random.choice([True, False]):
            Project.objects.create(
                user=username,
                title=f"{random.choice(TITLES)} - {random.randint(1,99)}",
                description=fake.paragraph(nb_sentences=3),
                tags=profile.skills,
                github_link=profile.github_url,
                no_of_stars=random.randint(0, 50),
            )
    print("Done!")


if __name__ == "__main__":
    create_users(20)
