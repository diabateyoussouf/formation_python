"""
==============================================================================
📦 C'EST QUOI LE FORMAT JSON ET POURQUOI EST-IL INDISPENSABLE EN IOT ?
==============================================================================
JSON (JavaScript Object Notation) est le "langage universel" d'échange de 
données sur Internet.

1. POURQUOI LE FORMAT JSON ?
   Un téléphone (Android/iOS), un capteur industriel (ESP32/Arduino) et un 
   serveur Python n'utilisent pas le même langage de programmation. 
   Pour communiquer sans erreur, tous ces équipements traduisent leurs données 
   dans une langue commune : un texte structuré ultra-léger appelé JSON.

2. À QUOI ÇA RESSEMBLE ?
   C'est la copie presque exacte d'un Dictionnaire Python (clé : valeur) :
   {
       "sensor_id": "PHONE_01",
       "puissance_w": 1250.5,
       "batterie_pct": 88
   }

3. L'ANALOGIE DU BON DE COMMANDE :
   Si vous envoyez un message vocal brut à un serveur, il ne le comprendra pas. 
   Le JSON est le BON DE COMMANDE imprimé de manière lisible et claire que le 
   capteur tend à l'API.

==============================================================================
🤔 C'EST QUOI UNE API ? (L'ANALOGIE DU RESTAURANT)
==============================================================================
Si vous n'avez jamais entendu parler d'API, imaginez un RESTAURANT :

1. LE CLIENT (Smartphone / Capteur) : 
   Assis à une table, il veut transmettre ou demander de l'information, mais 
   n'a pas le droit d'entrer directement dans la cuisine.

2. LA CUISINE (Base de Données SQLite) : 
   Endroit où sont stockées et préparées toutes les données.

3. LE SERVEUR DE SALLE (L'API / FastAPI) : 
   L'INTERMÉDIAIRE OBLIGATOIRE. 
   - Il apporte le menu à consulter (la documentation /docs).
   - Il reçoit le bon de commande au format JSON envoyé par le client.
   - Il vérifie si la commande est valide (Validation Pydantic).
   - Il transmet l'ordre en cuisine (Écriture SQL via utilis.py).
   - Il confirme la bonne réception au client (Réponse HTTP 200/201).

==============================================================================
🌐 ARCHITECTURE DU PROJET
==============================================================================
📱 Smartphone / Capteur IoT
    │
    │ 1. Envoie une trame JSON par le réseau (HTTP POST)
    ▼
🚀 FastAPI - main.py (Valide le JSON & contrôle les accès)
    │
    │ 2. Transmet les valeurs propres à la BDD
    ▼
💾 Base SQLite - iot_energie.db (Stockage via utilis.py)
    ▲
    │ 3. Lit la BDD pour actualiser les graphiques
    │
⚡ Dashboard Streamlit - app.py (Supervision temps réel)

==============================================================================
🛠️ CONSIGNES ET DÉMARRAGE
==============================================================================
0. Installer dependances de fast api et pydantic :
   uv add fastapi pydantic
1. Commande de démarrage dans le terminal :
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

2. Tester et visualiser les structures JSON dans Swagger UI :
   http://localhost:8000/docs

3. Exercices : Complétez les Niveaux 00 à 15 en remplaçant chaque '...'.
==============================================================================
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status # permet d'utiliser les codes de statut HTTP
from fastapi.middleware.cors import CORSMiddleware # permet d'autoriser les requêtes provenant d'autres domaines (CORS)
from datetime import datetime
from pydantic import BaseModel, Field # permet de définir des modèles de données pour la validation et la sérialisation

import utilis

# Initialisation de la BDD SQLite
utilis.init_db()

# Instanciation de l'API FastAPI
app = FastAPI(
    title="Passerelle API IoT Smart Grid",
    description="Serveur intermédiaire de validation JSON et réception réseau.",
    version="1.0.0",
)
# ==============================================================================
# 🟢 NIVEAU 00 : CONCEPT D'API REST & INSTANCIATION
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 00 : QU'EST-CE QU'UNE API REST ?
----------------------------------------------------------------------------
Une API (Application Programming Interface) permet à deux programmes 
(ex: un téléphone et un serveur) de communiquer via le protocole HTTP(sert de pont de communication).
FastAPI est le framework Python le plus rapide pour construire des APIs REST.

Composants principaux :
- L'URL (Endpoint) : Adresse de la ressource.
- La Réponse JSON : Format standard d'échange de données léger { "cle": "valeur" }.
============================================================================
"""


"""
==============================================================================
🎓 CURSUS FASTAPI IOT — SUPPORT DE COURS & EXERCICES EN BATCH (PROJET 09)
==============================================================================
Instructions d'exécution :
0. Installer les dépendances dans votre terminal :
   uv add fastapi uvicorn pydantic
1. Lancez ce fichier depuis le dossier Projet_09_API_FastAPI :
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
2. Ouvrez votre navigateur pour tester la documentation interactive Swagger :
   http://localhost:8000/docs
3. Pour chaque niveau, lisez le cours rédigé en commentaire multi-lignes.
4. Complétez le code en remplaçant TOUS les '...' par la syntaxe exacte.
5. Sauvegardez le fichier (Ctrl+S), Uvicorn rechargera l'API automatiquement.
==============================================================================
"""


# ==============================================================================
# 🟢 NIVEAU 01 : INITIALISATION FASTAPI & ROUTE DE DIAGNOSTIC (GET)
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 01 : LES BASES DE FASTAPI & VERBE GET
----------------------------------------------------------------------------
FastAPI est un framework web moderne et rapide basé sur le typage Python.
Contrairement à un serveur classique, il génère automatiquement une 
documentation interactive Swagger disponible sur l'URL '/docs'.

FONCTIONS ET DÉCORATEURS À RÉVISER :
1. app = FastAPI()
   - Instancie le serveur d'application.
2. @app.get("/chemin")
   - Décorateur de route capturant les requêtes HTTP GET (lecture de données).
3. Dictionnaires Python
   - FastAPI convertit automatiquement les dictionnaires renvoyés par les 
     fonctions en réponses au format standard JSON.
============================================================================
"""


# ÉTAPE : Créer une route GET sur la racine "/" pour vérifier l'état de l'API
@app....("/")  # <--- Décorateur pour écouter les requêtes GET sur la racine
def racine():
    return {
        "systeme": "Smart Grid IoT Gateway",
        "statut": "online",
        "horodatage": datetime.now().isoformat(),
    }


# ==============================================================================
# 🟢 NIVEAU 02 : PARAMÈTRES DE ROUTE ET DE REQUÊTE (GET)
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 02 : TRANSMISSION DE PARAMÈTRES VIA L'URL
----------------------------------------------------------------------------
L'API doit pouvoir filtrer des informations spécifiques transmises par l'URL.

DEUX TYPES DE PARAMÈTRES :
1. Paramètres de chemin (Path Parameters) :
   - Inscrits directement dans l'URL : @app.get("/capteurs/{sensor_id}")
   - Indispensables pour cibler une ressource précise par son identifiant.
2. Paramètres de requête (Query Parameters) :
   - Passés après le '?' dans l'URL (ex: /capteurs/CAP_01?limit=10)
   - Déclarés comme arguments standard dans la fonction Python.
============================================================================
"""


# ÉTAPE : Créer une route acceptant un paramètre de chemin {sensor_id} et un query parameter limit
@app.get("/api/capteurs/{sensor_id}")
def lire_capteur_par_id(sensor_id: str, limit: int = 5):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Requête SQL paramétrée
    cursor.execute(
        "SELECT * FROM telemetrie_energie WHERE sensor_id = ? ORDER BY id DESC LIMIT ?",
        (sensor_id, limit),
    )
    mesures = cursor.fetchall()
    conn.close()

    return {
        "sensor_id": ...,  # <--- Renvoyer la variable du chemin
        "nombre_resultats": len(mesures),
        "trames": mesures,
    }


# ==============================================================================
# 🟢 NIVEAU 03 : VALIDATION DE DONNÉES AVEC PYDANTIC (BASEMODEL)
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 03 : SCHÉMAS PYDANTIC & STRUCTURATION DES TRAMES
----------------------------------------------------------------------------
Pour garantir que les nœuds IoT (smartphones, capteurs) envoient des données 
valides, FastAPI s'appuie sur la librairie Pydantic.

CONCEPTS CLÉS :
1. BaseModel
   - Classe parente permettant de définir la structure JSON attendue.
2. Typer les attributs
   - sensor_id: str
   - puissance_w: float
   - Si une trame reçue ne respecte pas ces types, FastAPI rejette 
     automatiquement la requête avec une erreur 422 (Unprocessable Entity).
============================================================================
"""


# ÉTAPE : Définir la classe Pydantic pour valider le corps (body) du JSON reçu
class TrameIoT(...):  # <--- Hériter de BaseModel de Pydantic
    sensor_id: str
    puissance_w: float
    tension_v: float
    timestamp: Optional[str] = None  # Optionnel, généré auto si omis


# ==============================================================================
# 🟢 NIVEAU 04 : INGESTION HTTP POST & INSERTION SQLITE
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 04 : ÉCRITURE EN BASE VIA LE VERBE POST
----------------------------------------------------------------------------
Les équipements IoT envoient leurs mesures via des requêtes HTTP POST. 
FastAPI décode le JSON, le valide via Pydantic et le met à disposition.

PROCÉDURE :
1. Décorateur @app.post("/route")
2. Injecter le schéma Pydantic comme argument de la fonction.
3. Exécuter l'INSERT SQL avec sqlite3.
============================================================================
"""


# ÉTAPE 1 : Déclarer la route POST pour l'ingestion des trames
@app....("/api/telemetrie")  # <--- Décorateur pour le verbe POST
def recevoir_trame(trame: TrameIoT):  # <--- Utiliser le schéma Pydantic
    date_mesure = trame.timestamp or datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ÉTAPE 2 : Insérer les valeurs de l'objet Pydantic 'trame' dans SQLite
    cursor.execute(
        """
        INSERT INTO telemetrie_energie (sensor_id, timestamp, puissance_w, tension_v)
        VALUES (?, ?, ?, ?);
        """,
        (
            trame....,  # <--- Récupérer l'attribut sensor_id
            date_mesure,
            trame....,  # <--- Récupérer l'attribut puissance_w
            trame.tension_v,
        ),
    )
    conn.commit()
    conn.close()

    return {"statut": "succès", "message": f"Trame reçue pour {trame.sensor_id}"}


# ==============================================================================
# 🟢 NIVEAU 05 : EXTRACTION SQL ET API DE CONSULTATION (GET)
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 05 : EXPOSER LA BASE DE DONNÉES EN JSON
----------------------------------------------------------------------------
Cette route permet à une application cliente (ex: Streamlit) de consommer 
l'ensemble des données enregistrées en BDD sous forme d'une liste d'objets JSON.

CONVERSION TUPLE -> DICTIONNAIRE :
sqlite3 renvoie des tuples (ex: (1, 'CAP_01', '2026-09-03', 1200.0, 230.0)).
Pour créer un JSON propre, on convertit chaque tuple en dictionnaire.
============================================================================
"""


@app.get("/api/telemetrie/toutes")
def extraire_toutes_telemetries():
    conn = sqlite3.connect(DB_FILE)
    # Permet de récupérer les résultats sous forme de dictionnaire clé:valeur
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM telemetrie_energie ORDER BY timestamp DESC LIMIT 50;"
    )
    lignes = cursor.fetchall()
    conn.close()

    # ÉTAPE : Convertir chaque ligne sqlite3.Row en dictionnaire Python
    resultats = [dict(...) for ligne in lignes]  # <--- Passer 'ligne' dans dict()

    return {"total": len(resultats), "donnees": resultats}


# ==============================================================================
# 🟢 NIVEAU 06 : MIDDLEWARE CORS, CODES STATUT & GESTION D'ERREURS
# ==============================================================================
"""
============================================================================
📖 COURS NIVEAU 06 : SÉCURITÉ, CORS & ERREURS HTTP
----------------------------------------------------------------------------
1. Cross-Origin Resource Sharing (CORS) :
   Par défaut, les navigateurs et smartphones bloquent les requêtes vers une API
   hébergée sur une autre adresse IP. On ajoute le middleware CORS pour lever 
   cette restriction.
2. HTTPException :
   Permet d'interrompre le traitement et de retourner un code erreur standard
   (ex: 404 Not Found, 500 Internal Server Error).
============================================================================
"""

# ÉTAPE 1 : Configuration CORS pour autoriser l'accès depuis le smartphone ou Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (IPs)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise tous les verbes HTTP (GET, POST, etc.)
    allow_headers=["*"],
)


# ÉTAPE 2 : Route sécurisée avec levée d'exception en cas de capteur inconnu
@app.get("/api/capteurs/stats/{sensor_id}")
def obtenir_stats_capteur(sensor_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(puissance_w), MAX(puissance_w) FROM telemetrie_energie WHERE sensor_id = ?",
        (sensor_id,),
    )
    row = cursor.fetchone()
    conn.close()

    # Si le capteur n'a aucune donnée enregistrée
    if row[0] is None:
        # ÉTAPE 3 : Lever une exception HTTP 404 avec la classe HTTPException
        raise ...(  # <--- Utiliser HTTPException
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune mesure trouvée pour le capteur {sensor_id}",
        )

    return {
        "sensor_id": sensor_id,
        "puissance_moyenne": round(row[0], 2),
        "puissance_max": row[1],
    }

# Pour visuliser le server fastapi, lancer la commande uvicorn main:app --reload --host
"""
Et accéder à l'url http://localhost:8000/docs pour voir la documentation interactive Swagger UI.
"""
# Visualisation du dashabord
"""
Pour visualiser le dashboard, laisser le serveur FastAPI tourner et lancer la commande streamlit run app.py sur un 2eme terminal. 
Ensuite, accéder à l'url http://localhost:8501 pour voir le dashboard.

"""
# Valeur ajoutée :
"""
Ajouter votre propre logique métier dans le fichier utilis.py pour enrichir les fonctionnalités de l'API et du dashboard 
Et d'autres apis pour la gestion des capteurs, la récupération de données historiques,la suppression ... etc.
"""