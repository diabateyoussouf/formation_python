# ⚡ Formation Python : Data Engineering & Analyse Énergétique IoT

Bienvenue dans le dépôt officiel de la formation **Python appliquée à la Data & l'Énergie IoT** !

---

## 🎯 But de la Formation

Cette formation pratique et progressive a pour objectif de vous former au métier d'**Ingénieur Data & Analyste Énergétique**. 

À travers des projets inspirés de cas industriels réels (centrales photovoltaïques, capteurs IoT, audits d'efficacité énergétique), vous apprendrez à :

* 🧹 **Nettoyer et préparer des données brutes** : Détection et suppression des doublons, correction des types de données, gestion des valeurs manquantes (`NaN`) et filtrage des aberrations capteurs (méthode IQR et bornes physiques).
* 📐 **Manipuler des séries temporelles** : Calculs vectorisés avec **NumPy** & **Pandas**, lissage par fenêtres glissantes (`.rolling()`), réséchantillonnage temporel et agrégations complexes (`groupby`).
* ☀️ **Appliquer des modèles physiques métier** : Normalisation du rendement aux conditions standards STC ($25^\circ\text{C}$), calcul du *Performance Ratio* ($PR$) et bilans d'énergie produite ($kWh$).
* 📊 **Créer des Dashboards d'Audit** : Visualisation claire et professionnelle des signaux et indicateurs clés (KPI) avec **Matplotlib** & **Seaborn**.
* 🤖 **Modéliser et Prédire** : Entraînement de modèles de régression linéaire avec **Scikit-Learn** pour créer des jumeaux numériques de production.

---

## 📁 Structure du Répertoire

Le projet est découpé en modules progressifs organisés sous forme de quêtes pratiques :

| Dossier / Projet | Description & Objectifs |
| :--- | :--- |
| **`Projet_01_IoT_Energie/`** | **Bases & Ingestion** : Prise en main des structures de données pour l'énergie IoT. |
| **`Projet_02_IoT_Energie/`** | **Analyse & Visualisation** : Exploration de signaux capteurs et premiers graphiques. |
| **`Projet_03_IoT_Energie/`** | **Consolidation Data Energy** : Pipeline de nettoyage (doublons, typage, imputation, `groupby`). |
| **`Projet_04_IoT_Energie/`** | **Audit & Performance Solaire** : Traitement avancé, correction STC, lissage temporel et régression prédictive. |

---

## 🚀 Guide d'Installation & de Démarrage

### 1. Télécharger le projet

**Option A : Avec Git (Recommandé)**
```bash
git clone [https://github.com/diabateyoussouf/formation_python.git](https://github.com/diabateyoussouf/formation_python.git)
cd formation_python
```
**Option B : En fichier ZIP**

1. Cliquez sur le bouton vert <> Code en haut à droite de cette page GitHub.

2. Cliquez sur Download ZIP.

3. Extrayez l'archive sur votre ordinateur, puis ouvrez un terminal dans le dossier extrait.

### 2. Installer l'environnement & les dépendances
⚡ Méthode 1 : Avec uv (Ultra rapide & Recommandé)
Si vous utilisez le gestionnaire de paquets `uv` :
`uv sync`
**🐍 Méthode 2 : Avec Python classique (pip & venv)**
# 1. Créer l'environnement virtuel
python -m venv .venv

# 2. Activer l'environnement virtuel
# Sur Windows :
`.venv\Scripts\activate`
# Sur macOS / Linux :
`source .venv/bin/activate`

## 3. Installer les dépendances du projet
`pip install -e .`
## 3. Travailler sur un TP / Projet dans VS Code
Ouvrez le dossier principal formation_python dans VS Code.

Allez dans le dossier du TP sur lequel vous souhaitez travailler (ex: Projet_04_IoT_Energie/).

Ouvrez le fichier notebook (.ipynb) ou script (.py).

Dans VS Code, sélectionnez l'environnement .venv comme Kernel Python (en haut à droite du notebook).

Exécutez les cellules pas à pas pour valider vos quêtes !

### 🛠️ Stack Technique
Langage : Python 3.10+

Gestionnaire de dépendances : uv / pip (pyproject.toml, uv.lock)

Analyse de données : pandas, numpy

Visualisation : matplotlib, seaborn

Machine Learning : scikit-learn
