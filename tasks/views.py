from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import ShowForm, TaskForm
from .models import Task, Show
import requests
import uuid



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
# 🔴 PARTIE 2 — AUTHENTIFICATION INTERNE
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
# 🔵 PARTIE 2 BIS — FRANCECONNECT (v1)
# ============================================================

FC_BASE = "https://fcp.integ01.dev-franceconnect.fr/api/v1"

CLIENT_ID = "211286433e39cce01db448d80181bdfd005554b19cd51b3fe7943f6b3b86ab6e"
CLIENT_SECRET = "2791a731e6a59f56b6b4dd0d08c9b1f593b5f3658b9fd731cb24248e2669af4b"

# ⚠️ IMPORTANT : Django doit tourner sur un port autorisé (3000, 4242, 8080, 1337)
REDIRECT_URI = "http://localhost:3000/callback"
POST_LOGOUT_REDIRECT = "http://localhost:3000/logout"


# -----------------------------
# 1) Redirection vers FranceConnect
# -----------------------------
def fc_login(request):
    state = uuid.uuid4().hex
    nonce = uuid.uuid4().hex

    request.session["fc_state"] = state
    request.session["fc_nonce"] = nonce

    authorize_url = (
        f"{FC_BASE}/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=openid%20profile&"   # <-- le & manquait ici
        f"state={state}&"
        f"nonce={nonce}"
    )

    return redirect(authorize_url)

    return redirect(authorize_url)


# -----------------------------
# 2) Callback FranceConnect
# -----------------------------
def fc_callback(request):
    code = request.GET.get("code")

    # Échange du code contre un token
    token_response = requests.post(
        f"{FC_BASE}/token",
        data={
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        }
    ).json()

    access_token = token_response.get("access_token")

    # Récupération des infos utilisateur
    userinfo = requests.get(
        f"{FC_BASE}/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    sub = userinfo.get("sub")  # identifiant unique FranceConnect

    # Création automatique du compte si nécessaire
    user, created = User.objects.get_or_create(
        username=sub,
        defaults={"password": User.objects.make_random_password()}
    )

    # Connexion automatique
    login(request, user)

    return redirect("watchlist")


# -----------------------------
# 3) Déconnexion FranceConnect
# -----------------------------
def fc_logout(request):
    logout(request)
    logout_url = (
        f"{FC_BASE}/logout?"
        f"post_logout_redirect_uri={POST_LOGOUT_REDIRECT}"
    )
    return redirect(logout_url)


# ============================================================
# 🔴 PARTIE 3 — WATCHLIST + TMDB
# ============================================================

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNDViZTcxYzc5MDc2NzBmMjNlODlkYTM3ODE3ZTJmMiIsIm5iZiI6MTc3MTMxNjA1My41ODA5OTk5LCJzdWIiOiI2OTk0MjM1NWM1MDllNTVjMmMxMjRlMWYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.8AsMFiuYj4xQyJg9uOV2Nn9dfw84pUQHO4SqpEg3HUw"
BASE_URL = "https://api.themoviedb.org/3/discover/tv"
HEADERS = {"Authorization": f"Bearer {TMDB_TOKEN}"}


@login_required
def watchlist(request):
    shows = Show.objects.filter(user=request.user)
    return render(request, "tasks/list.html", {"shows": shows})


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
            poster_path = show.get("poster_path")

            if not Show.objects.filter(tmdb_id=tmdb_id, user=request.user).exists():
                Show.objects.create(
                    title=title,
                    tmdb_id=tmdb_id,
                    provider=provider_name,
                    poster_path=poster_path,
                    user=request.user
                )
                added += 1

            if added >= 10:
                break

    request.session[session_key] = page
    return redirect("watchlist")


@login_required
def add_netflix_shows(request):
    return add_shows(request, 8, "Netflix", "netflix_page")


@login_required
def add_prime_shows(request):
    return add_shows(request, 119, "Prime Video", "prime_page")


@login_required
def add_apple_shows(request):
    return add_shows(request, 350, "Apple TV", "apple_page")


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
