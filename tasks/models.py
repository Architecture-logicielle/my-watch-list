from django.db import models

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
    tmdb_id = models.IntegerField(unique=True)
    provider = models.CharField(max_length=50)

    def __str__(self):
        return self.title
