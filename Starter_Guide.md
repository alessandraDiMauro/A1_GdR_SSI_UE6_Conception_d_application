# Guide de Démarrage Rapide : Projet SI Barrage

Bienvenue dans le projet SI Barrage ! Ce guide est conçu pour vous aider à prendre en main le projet, de l'installation à votre toute première modification du code.

## Prérequis

Avant de commencer, assurez-vous d'avoir git installé sur votre machine :

* [Git](https://git-scm.com/) pour le contrôle de version.

## 1. Cloner le projet

Pour commencer, ouvrez un terminal et clonez le dépôt Git du projet sur votre machine locale :

```shell
git clone https://github.com/draner/A1_GdR_SSI_UE6_Conception_d_application.git
cd A1_GdR_SSI_UE6_Conception_d_application  # Assurez-vous d'être dans le bon dossier
```

## 2. Mettre en place l'environnement de développement

Nous utilisons `uv` pour gérer notre environnement virtuel et nos dépendances.

### a. Installer `uv`

Si vous ne l'avez pas encore, installez `uv` avec la commande suivante :

```shell
# macOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### b. Créer l'environnement virtuel

Depuis la racine du projet, créez un environnement virtuel qui contiendra toutes les dépendances nécessaires :

```shell
uv sync
```

## 3. Lancer l'application

Une fois l'environnement prêt, vous pouvez lancer le serveur de développement FastAPI :

```shell
uv run uvicorn si_barrage.main:app --reload
```

Cette commande démarre le serveur avec l'option `--reload`, qui redémarrera automatiquement l'application à chaque modification de fichier.

L'API est maintenant accessible à l'adresse [http://127.0.0.1:8000](http://127.0.0.1:8000). Vous pouvez ouvrir ce lien dans votre navigateur pour voir le message de bienvenue.

## 4. Votre première modification du code

Maintenant que tout est en place, il est temps de faire votre première contribution ! Nous allons ajouter un nouveau point de terminaison (endpoint) à notre API.

### a. Ouvrir le fichier `main.py`

Ouvrez le fichier `si_barrage/main.py` dans votre éditeur de code préféré.

### b. Ajouter un nouvel endpoint

Repérez la fonction `read_root` dans le fichier `si_barrage/main.py`, et ajoutez le code pour votre nouveau point de terminaison juste en dessous.

```python
@app.get("/hello", tags=["Greetings"])
def read_hello():
    """
    Un point de terminaison qui retourne un salut amical.
    """
    return {"message": "Hello there, General Kenobi !"}
```

Le résultat final devrait ressembler à ceci :

```python
# ...

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API du SI Barrage"}


@app.get("/hello", tags=["Greetings"])
def read_hello():
    """
    Un point de terminaison qui retourne un salut amical.
    """
    return {"message": "Hello there, General Kenobi !"}
```

### c. Vérifier votre modification

Si le serveur `uvicorn` est toujours en cours d'exécution, il se rechargera automatiquement. Sinon, relancez-le.

Ouvrez votre navigateur et allez à l'URL [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). C'est l'interface de documentation automatique de FastAPI. Vous devriez y voir votre nouveau point de terminaison `/hello` dans la section "Greetings".

Cliquez dessus pour le tester et voir la réponse `{"message": "Hello there, General Kenobi !"}`.

## 5. Écrire et lancer un test

Tester son code est une étape cruciale pour s'assurer de sa qualité et éviter les régressions. Nous allons ajouter un test pour le point de terminaison `/hello` que vous venez de créer.

### a. Installer les dépendances de test

Nous avons défini des dépendances spécifiques pour les tests. Installez-les avec `uv` :

```shell
uv pip install -e ".[test]"
```
Cela installera `pytest`, un lanceur de tests populaire, et `httpx` pour envoyer des requêtes à notre API dans les tests.

### b. Créer le fichier de test

Créez un nouveau fichier nommé `si_barrage/tests/test_main.py`. Le nom du fichier doit commencer par `test_` pour que `pytest` le découvre automatiquement.

### c. Écrire le test

Ouvrez le fichier `si_barrage/tests/test_main.py` et ajoutez le code suivant :

```python
from fastapi.testclient import TestClient
from si_barrage.main import app

# Crée un client de test pour notre application FastAPI
client = TestClient(app)

def test_read_hello():
    """
    Vérifie que le point de terminaison /hello fonctionne correctement.
    """
    # Envoie une requête GET à l'endpoint /hello
    response = client.get("/hello")
    
    # Vérifie que le code de statut est 200 (OK)
    assert response.status_code == 200
    
    # Vérifie que le contenu de la réponse est correct
    assert response.json() == {"message": "Hello there, General Kenobi !"}

def test_read_root():
    """
    Vérifie le point de terminaison racine.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API du SI Barrage"}
```

Ce test utilise le `TestClient` de FastAPI pour simuler des requêtes à notre application sans avoir besoin de lancer un serveur réel.

### d. Lancer les tests

Maintenant, pour lancer tous les tests du projet, exécutez la commande `uv run pytest` à la racine du projet :

```shell
pytest
```

`pytest` va automatiquement trouver et exécuter tous les tests dans le dossier `si_barrage/tests`. Si tout se passe bien, vous devriez voir un message indiquant que les tests ont réussi !

## Et après ?

Félicitations ! Vous avez cloné, configuré et modifié le projet avec succès.

Vous êtes maintenant prêt à explorer le reste du code. N'hésitez pas à consulter les fichiers suivants pour mieux comprendre la structure du projet :

* `README.md`: Le fichier principal de présentation du projet.
* `ARCHITECTURE.md`: Une description de l'architecture logicielle du projet.
* `si_barrage/`: Le cœur de l'application FastAPI.

Bon code !
