# ---------------------------------------------------------
# 1) Image de base : Python 3.13.3 (version utilisée localement)
# ---------------------------------------------------------
FROM python:3.13.3-slim

# ---------------------------------------------------------
# 2) Optimisations Python :
# - Ne pas générer de fichiers .pyc
# - Afficher les logs immédiatement (pas de buffer)
# ---------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------------------------------------------------
# 3) Définir le dossier de travail dans le container
# ---------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------
# 4) Copier les dépendances et les installer
# ---------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👉 AJOUT IMPORTANT : installer psycopg2-binary
RUN pip install psycopg2-binary

# ---------------------------------------------------------
# 5) Copier tout le code du projet dans le container
# ---------------------------------------------------------
COPY . .

# ---------------------------------------------------------
# 6) Exposer le port 8000 (port utilisé par Gunicorn)
# ---------------------------------------------------------
EXPOSE 8000

# ---------------------------------------------------------
# 7) Lancer l'application Django avec Gunicorn (production)
# ---------------------------------------------------------
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "todo.wsgi:application"]
