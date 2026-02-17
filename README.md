# 🎬 My Watch List
Application Django permettant de gérer une watchlist personnalisée et d’ajouter automatiquement des séries depuis l’API TMDB (Netflix, Prime Video, Apple TV).

---

## 📌 Fonctionnalités

### ✔️ Partie 1 — To‑Do List (héritée du projet initial)
- Création, mise à jour et suppression de tâches
- Interface simple et fonctionnelle

### ✔️ Partie 2 — Watchlist avec TMDB
- Intégration de l’API TMDB (Discover TV)
- Ajout automatique de séries :
  - 10 séries Netflix
  - 10 séries Prime Video
  - 10 séries Apple TV
- Pagination dynamique : chaque clic ajoute **10 nouvelles séries différentes**
- Gestion des doublons via `tmdb_id`
- Interface moderne pastel (style Netflix revisité)

---

## 🛠️ Technologies utilisées
- **Python 3**
- **Django 5**
- **Bootstrap 4**
- **API TMDB (The Movie Database)**

---

## 🚀 Installation & lancement

### 1. Cloner le projet
```bash
git clone https://github.com/<ton-nom>/my-watch-list.git
cd my-watch-list

![alt text](image.png)