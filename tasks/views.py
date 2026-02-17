from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import ShowForm, TaskForm
from .models import *
from .forms import *
import requests

# ============================================================
# 🔵 PARTIE 1 — ANCIENNES VUES (TO DO LIST)
# ============================================================

def index(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')

    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/list.html', context)


def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)


def deleteTask(request, pk):
    item = Task.objects.get(id=pk)

    if request.method == "POST":
        item.delete()
        return redirect('/')

    context = {'item': item}
    return render(request, 'tasks/delete.html', context)


# ============================================================
# 🔴 PARTIE 2 — NOUVELLES VUES (WATCHLIST NETFLIX)
# ============================================================

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNDViZTcxYzc5MDc2NzBmMjNlODlkYTM3ODE3ZTJmMiIsIm5iZiI6MTc3MTMxNjA1My41ODA5OTk5LCJzdWIiOiI2OTk0MjM1NWM1MDllNTVjMmMxMjRlMWYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.8AsMFiuYj4xQyJg9uOV2Nn9dfw84pUQHO4SqpEg3HUw"
BASE_URL = "https://api.themoviedb.org/3/discover/tv"

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}"
}

# -----------------------------
# PAGE PRINCIPALE : WATCHLIST
# -----------------------------
def watchlist(request):
    shows = Show.objects.all()   # pas de user pour l'instant
    form = ShowForm()

    if request.method == "POST":
        form = ShowForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("watchlist")

    context = {"shows": shows, "form": form}
    return render(request, "tasks/list.html", context)


# -----------------------------
# FONCTION UTILITAIRE TMDB
# -----------------------------
def fetch_tmdb_shows(provider_id):
    params = {
        "with_watch_providers": provider_id,
        "watch_region": "FR",
        "sort_by": "vote_average.desc",
        "page": 1
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    return response.json().get("results", [])[:10]


# -----------------------------
# PROVIDERS TMDB
# -----------------------------
def add_netflix_shows(request):
    data = fetch_tmdb_shows(8)  # Netflix
    for show in data:
        tmdb_id = show["id"]
        title = show["name"]

        if not Show.objects.filter(tmdb_id=tmdb_id).exists():
            Show.objects.create(
                title=title,
                tmdb_id=tmdb_id,
                provider="Netflix"
            )
    return redirect("watchlist")


def add_prime_shows(request):
    data = fetch_tmdb_shows(119)  # Prime Video
    for show in data:
        tmdb_id = show["id"]
        title = show["name"]

        if not Show.objects.filter(tmdb_id=tmdb_id).exists():
            Show.objects.create(
                title=title,
                tmdb_id=tmdb_id,
                provider="Prime Video"
            )
    return redirect("watchlist")


def add_apple_shows(request):
    data = fetch_tmdb_shows(350)  # Apple TV
    for show in data:
        tmdb_id = show["id"]
        title = show["name"]

        if not Show.objects.filter(tmdb_id=tmdb_id).exists():
            Show.objects.create(
                title=title,
                tmdb_id=tmdb_id,
                provider="Apple TV"
            )
    return redirect("watchlist")


# -----------------------------
# CRUD WATCHLIST
# -----------------------------
def update_show(request, pk):
    show = Show.objects.get(id=pk)
    form = ShowForm(instance=show)

    if request.method == "POST":
        form = ShowForm(request.POST, instance=show)
        if form.is_valid():
            form.save()
            return redirect("watchlist")

    return render(request, "tasks/update_task.html", {"form": form})


def delete_show(request, pk):
    show = Show.objects.get(id=pk)

    if request.method == "POST":
        show.delete()
        return redirect("watchlist")

    return render(request, "tasks/delete.html", {"item": show})
