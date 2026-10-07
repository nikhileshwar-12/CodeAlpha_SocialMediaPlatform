"""
Populate the database with demo users, follows, posts, comments and likes.

Usage:
    python manage.py seed_data
"""
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Follow, Profile
from posts.models import Comment, Like, Post

DEMO_PASSWORD = "demo12345"

USERS = [
    ("aarav", "Aarav Sharma", "Full-stack dev ☕ | Building things with Django & JS", "Hyderabad, India"),
    ("diya", "Diya Patel", "UI/UX designer 🎨 Coffee, colours and clean layouts.", "Bengaluru, India"),
    ("kabir", "Kabir Mehta", "Photographer 📸 Chasing golden hours.", "Mumbai, India"),
    ("meera", "Meera Iyer", "Data science student 📊 | Runner 🏃‍♀️", "Chennai, India"),
    ("rohan", "Rohan Verma", "Gamer, gadget reviewer and part-time chef 🍳", "Delhi, India"),
    ("sana", "Sana Khan", "Travel blogger ✈️ 30 countries and counting", "Pune, India"),
]

POSTS = [
    ("aarav", "Just finished building a session-based shopping cart in Django. Surprisingly elegant once you get the hang of it! 🛒"),
    ("aarav", "Hot take: writing tests first actually saves time. Fight me. 🧪"),
    ("diya", "New portfolio redesign is live! Went with a soft pastel palette this time. Thoughts?"),
    ("diya", "Reminder: whitespace is not empty space, it's breathing room. ✨"),
    ("kabir", "Shot this morning at Marine Drive. The light at 6am is unreal."),
    ("kabir", "Film vs digital debate again in the group chat. Both, obviously. 🎞️"),
    ("meera", "Finally understood how gradient descent works by drawing it by hand. Pen and paper > slides."),
    ("meera", "10k run done before breakfast. Legs are complaining, brain is happy. 🏃‍♀️"),
    ("rohan", "Reviewed the new mechanical keyboard - those tactile switches are *chef's kiss* ⌨️"),
    ("rohan", "Made butter chicken from scratch tonight. The kitchen looks like a crime scene but worth it."),
    ("sana", "Country #31: Vietnam! The street food in Hanoi is on another level 🍜"),
    ("sana", "Travel tip: always keep a photocopy of your passport in a separate bag. Learned the hard way."),
    ("aarav", "Weekend plan: refactor the notifications module and finally fix that flaky test."),
    ("diya", "Designed a dark mode for the app today. My eyes say thank you."),
    ("meera", "Anyone else find SQL window functions weirdly satisfying?"),
]

COMMENTS = [
    "Love this! 🔥",
    "Totally agree.",
    "Can you share more details?",
    "This made my day 😄",
    "Great work, keep it up!",
    "Bookmarking this.",
    "Haha, relatable.",
    "Inspiring as always ✨",
]

FOLLOWS = [
    ("aarav", ["diya", "kabir", "meera"]),
    ("diya", ["aarav", "sana"]),
    ("kabir", ["diya", "sana", "rohan"]),
    ("meera", ["aarav", "rohan"]),
    ("rohan", ["kabir", "meera", "sana", "aarav"]),
    ("sana", ["kabir", "diya"]),
]


class Command(BaseCommand):
    help = "Seed the database with demo users, posts, comments, likes and follows"

    def handle(self, *args, **options):
        random.seed(42)
        users = {}
        for username, full_name, bio, location in USERS:
            first, _, last = full_name.partition(" ")
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@example.com"},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio, profile.location = bio, location
            profile.save()
            users[username] = user
        self.stdout.write(self.style.SUCCESS(f"Users ready: {', '.join(users)} (password: {DEMO_PASSWORD})"))

        for follower, targets in FOLLOWS:
            for target in targets:
                Follow.objects.get_or_create(follower=users[follower], following=users[target])

        if Post.objects.count() == 0:
            posts = [Post.objects.create(author=users[u], content=text) for u, text in POSTS]
            all_users = list(users.values())
            for post in posts:
                for user in random.sample(all_users, k=random.randint(0, len(all_users))):
                    Like.objects.get_or_create(post=post, user=user)
                for user in random.sample(all_users, k=random.randint(0, 3)):
                    Comment.objects.create(post=post, author=user, text=random.choice(COMMENTS))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(posts)} posts, {Like.objects.count()} likes and {Comment.objects.count()} comments"
                )
            )
        else:
            self.stdout.write("Posts already exist - skipping post creation.")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123", first_name="Admin")
            self.stdout.write(self.style.SUCCESS("Demo admin created -> username: admin  password: admin123"))
