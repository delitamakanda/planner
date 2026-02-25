# Planner

Application **Django** (Python) pour gérer un planning avec plusieurs modules (comptes, projets, congés, etc.).  
Le dépôt contient un projet Django principal et plusieurs apps dédiées.

## Structure (vue rapide)

- `manage.py` : point d’entrée des commandes Django
- `planner/` : configuration du projet Django (settings/urls/asgi/wsgi)
- Apps Django (fonctionnalités) :
  - `accounts/` : gestion des utilisateurs / authentification (selon votre implémentation)
  - `api/` : endpoints API (si activés)
  - `planning/` : logique de planning (modèles, vues, migrations, admin…)
  - `projects/` : gestion des projets
  - `leaves/` : gestion des absences / congés
  - `common/` : éléments partagés (utils, constantes, mixins…)
- `db.sqlite3` : base SQLite locale (développement)
- `.env` : variables d’environnement (non à versionner en clair)
- `LICENSE` : licence du projet

## Prérequis

- **Python 3.14+**
- **virtualenv** (déjà prévu pour ce projet)
- (Optionnel) SQLite est intégré à Python, donc rien à installer pour le dev si vous restez sur `db.sqlite3`.

## Installation (développement)

1. **Cloner le dépôt** puis se placer à la racine (là où se trouve `manage.py`).

2. **Créer et activer un environnement virtuel** :
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances**  
   Si vous avez un fichier `requirements.txt` :
   ```bash
   pip install -r requirements.txt
   ```
   Sinon, installez au minimum :
   ```bash
   pip install django
   ```

4. **Configurer les variables d’environnement**
   - Créez/complétez le fichier `.env` à la racine du projet.
   - Exemple (à adapter à vos réglages) :
     ```env
     DJANGO_SECRET_KEY=<votre_valeur>
     DJANGO_DEBUG=true
     ```

## Lancer le projet

1. Appliquer les migrations :
   ```bash
   python manage.py migrate
   ```

2. Démarrer le serveur :
   ```bash
   python manage.py runserver
   ```

3. Ouvrir dans le navigateur :
   - http://127.0.0.1:8000/

## Commandes utiles

- Créer un superutilisateur (admin Django) :
  ```bash
  python manage.py createsuperuser
  ```

- Lancer les tests :
  ```bash
  python manage.py test
  ```

- Ouvrir l’admin (après création d’un superuser) :
  - http://127.0.0.1:8000/admin/

## Notes

- `db.sqlite3` est pratique pour le développement. Pour la production, il est recommandé d’utiliser une base dédiée (PostgreSQL, etc.) et une configuration plus stricte.
- Ne committez jamais de secrets : gardez les valeurs sensibles uniquement dans `.env` (ou un gestionnaire de secrets).
