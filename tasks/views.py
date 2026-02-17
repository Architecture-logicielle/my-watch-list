from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import ShowForm, TaskForm
from .models import Task, Show
import requests


# ============================================================
# 🔵 PARTIE 1 — TO DO LIST
# ============================================================

def index(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    return render(request, 'tasks/list.html', {'tasks': tasks, 'form': form})


def updateTask(request, pk):
    task = get_object_or_404(Task, id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    return render(request, 'tasks/update_task.html', {'form': form})


def deleteTask(request, pk):
    task = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        task.delete()
        return redirect('/')

    return render(request, 'tasks/delete.html', {'item': task})


# ============================================================
# 🔴 PARTIE 2 — AUTHENTIFICATION
# ============================================================

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("watchlist")

        return render(request, "auth/login.html", {"error": "Identifiants invalides"})

    return render(request, "auth/login.html")


def logout_user(request):
    logout(request)
    return redirect("login")


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {"error": "Nom déjà utilisé"})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("watchlist")

    return render(request, "auth/register.html")


# ============================================================
# 🔴 PARTIE 3 — WATCHLIST + TMDB
# ============================================================

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNDViZTcxYzc5MDc2NzBmMjNlODlkYTM3ODE3ZTJmMiIsIm5iZiI6MTc3MTMxNjA1My41ODA5OTk5LCJzdWIiOiI2OTk0MjM1NWM1MDllNTVjMmMxMjRlMWYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.8AsMFiuYj4xQyJg9uOV2Nn9dfw84pUQHO4SqpEg3HUw"
BASE_URL = "https://api.themoviedb.org/3/discover/tv"
HEADERS = {"Authorization": f"Bearer {TMDB_TOKEN}"}


# -----------------------------
# PAGE WATCHLIST
# -----------------------------
@login_required
def watchlist(request):
    shows = Show.objects.filter(user=request.user)
    return render(request, "tasks/list.html", {"shows": shows})


# -----------------------------
# FONCTION TMDB
# -----------------------------
def fetch_tmdb_shows(provider_id, page):
    params = {
        "with_watch_providers": provider_id,
        "watch_region": "FR",
        "sort_by": "vote_average.desc",
        "page": page
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json().get("results", [])
    return []


# -----------------------------
# AJOUT SHOWS (CORRIGÉ)
# -----------------------------
@login_required
def add_shows(request, provider_id, provider_name, session_key):
    page = request.session.get(session_key, 1)

    added = 0
    attempts = 0

    while added < 10 and attempts < 5:
        data = fetch_tmdb_shows(provider_id, page)
        page += 1
        attempts += 1

        for show in data:
            tmdb_id = show.get("id")
            title = show.get("name", "Unknown title")
            poster_path = show.get("poster_path")  # ✅ CORRECTION

            if not Show.objects.filter(tmdb_id=tmdb_id, user=request.user).exists():
                Show.objects.create(
                    title=title,
                    tmdb_id=tmdb_id,
                    provider=provider_name,
                    poster_path=poster_path,  # ✅ SAUVEGARDE IMAGE
                    user=request.user
                )
                added += 1

            if added >= 10:
                break

    request.session[session_key] = page
    return redirect("watchlist")


# -----------------------------
# PROVIDERS
# -----------------------------
@login_required
def add_netflix_shows(request):
    return add_shows(request, 8, "Netflix", "netflix_page")


@login_required
def add_prime_shows(request):
    return add_shows(request, 119, "Prime Video", "prime_page")


@login_required
def add_apple_shows(request):
    return add_shows(request, 350, "Apple TV", "apple_page")


# -----------------------------
# CRUD WATCHLIST
# -----------------------------
@login_required
def update_show(request, pk):
    show = get_object_or_404(Show, id=pk, user=request.user)
    form = ShowForm(instance=show)

    if request.method == "POST":
        form = ShowForm(request.POST, instance=show)
        if form.is_valid():
            form.save()
            return redirect("watchlist")

    return render(request, "tasks/update_task.html", {"form": form})


@login_required
def delete_show(request, pk):
    show = get_object_or_404(Show, id=pk, user=request.user)

    if request.method == "POST":
        show.delete()
        return redirect("watchlist")

    return render(request, "tasks/delete.html", {"item": show})
