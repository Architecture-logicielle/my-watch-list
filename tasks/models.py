from django.db import models
from django.contrib.auth.models import User

# -----------------------------
# 🔵 ANCIEN MODÈLE (TO DO LIST)
# -----------------------------
class Task(models.Model):
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -----------------------------
# 🔴 NOUVEAU MODÈLE (WATCHLIST)
# -----------------------------
class Show(models.Model):
    title = models.CharField(max_length=255)
    tmdb_id = models.IntegerField()
    provider = models.CharField(max_length=50)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title
