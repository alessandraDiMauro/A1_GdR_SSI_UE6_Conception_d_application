# Architecture du Projet et Structure des Fichiers

Ce document décrit l'architecture logicielle cible pour le projet "SI Barrage" et la manière dont le code source doit être organisé. Une structure claire et cohérente est essentielle pour la collaboration et l'intégration des différents modules.

## Architecture Générale

L'application est conçue comme un système modulaire. Chaque module correspond à une fonctionnalité métier principale (Météo, Maintenance, Production) et est développé par une équipe dédiée.

- **Application Principale (`main.py`) :** C'est le point d'entrée de l'application. Elle est responsable de :
  - L'initialisation de l'application FastAPI.
  - Le chargement et l'intégration des "routeurs" de chaque module.
  - La gestion de la connexion à la base de données.
  - L'affichage du menu principal (dans le cas d'une interface graphique).

- **Modules (`modules/`) :** Chaque module est un sous-répertoire dans le dossier `modules/`. Il encapsule la logique, les routes d'API et les services spécifiques à sa fonctionnalité. Cette approche modulaire permet de travailler en parallèle et de bien séparer les responsabilités.

- **Base de Données (`db.py`) :** Un script ou module central pour gérer la connexion à la base de données (SQLite en local, PostgreSQL en production) et potentiellement définir les modèles de données (par exemple, avec SQLAlchemy).

## Structure des Fichiers

Voici la structure de dossiers et de fichiers que vous devez suivre.

```
/si_barrage
│
├── main.py             # Point d'entrée de l'application FastAPI principale
├── db.py               # Configuration et connexion à la base de données
├── requirements.txt    # Dépendances Python du projet
│
├── modules/
│   │
│   ├── meteo/
│   │   ├── __init__.py
│   │   ├── router.py     # Endpoints de l'API pour la météo (ex: /meteo/releves)
│   │   └── services.py   # Logique métier (ex: calculer les prévisions)
│   │
│   ├── maintenance/
│   │   ├── __init__.py
│   │   ├── router.py     # Endpoints de l'API pour la maintenance (ex: /maintenance/tickets)
│   │   └── services.py   # Logique métier (ex: créer un ticket)
│   │
│   └── production/
│       ├── __init__.py
│       ├── router.py     # Endpoints de l'API pour la production (ex: /production/historique)
│       └── services.py   # Logique métier (ex: simuler la production)
│
├── tests/                # Dossier pour les tests unitaires et d'intégration
│   ├── test_meteo.py
│   ├── test_maintenance.py
│   └── test_production.py
│
└── assets/               # Ressources statiques (icônes, images, etc.) - Optionnel
```

### Description des Fichiers Clés

- **`main.py` :** Lance le serveur FastAPI. C'est ici que vous importerez et inclurez les routeurs de chaque module.
  ```python
  # Exemple dans main.py
  from fastapi import FastAPI
  from modules.meteo import router as meteo_router
  from modules.maintenance import router as maintenance_router
  from modules.production import router as production_router

  app = FastAPI(title="SI Barrage")

  app.include_router(meteo_router.router, prefix="/meteo", tags=["Météo"])
  app.include_router(maintenance_router.router, prefix="/maintenance", tags=["Maintenance"])
  app.include_router(production_router.router, prefix="/production", tags=["Production"])
  ```

- **`db.py` :** Gère la connexion à la base de données. Pour permettre une configuration facile entre SQLite et PostgreSQL, ce fichier pourrait contenir une fonction qui retourne une session de base de données.

- **`requirements.txt` :** Liste toutes les bibliothèques Python nécessaires au projet (ex: `fastapi`, `uvicorn`, `sqlalchemy`). Chaque membre de l'équipe doit pouvoir installer ces dépendances avec `pip install -r requirements.txt`.

- **`modules/<nom_module>/router.py` :** Contient les endpoints de l'API pour un module donné. Utilise `APIRouter` de FastAPI pour regrouper les routes.

- **`modules/<nom_module>/services.py` :** Contient la logique métier (les "fonctions intelligentes"). Par exemple, une fonction `creer_ticket_intervention()` dans `maintenance/services.py` qui prend des données en entrée, les valide, et les insère en base de données. Le routeur appelle les fonctions du service.

- **`tests/` :** Les tests sont cruciaux ! Chaque équipe est responsable d'écrire des tests pour son module afin de garantir son bon fonctionnement avant l'intégration.

Cette structure favorise la séparation des préoccupations et rendra votre projet plus facile à maintenir et à faire évoluer.