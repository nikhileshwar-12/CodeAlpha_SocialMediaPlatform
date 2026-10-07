from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.urls import reverse


class Profile(models.Model):
    """Extra information attached to Django's built-in User."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=300, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username}"

    def get_absolute_url(self):
        return reverse("accounts:profile", args=[self.user.username])

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def avatar_color(self):
        """Deterministic colour used for the initials avatar when no picture is uploaded."""
        hue = sum(ord(c) for c in self.user.username) % 360
        return f"hsl({hue}, 60%, 45%)"

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()


class Follow(models.Model):
    """`follower` follows `following`."""

    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(condition=~Q(follower=F("following")), name="prevent_self_follow"),
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.follower} → {self.following}"
