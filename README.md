# Web Scraping Project Beautifulsoup

Ce projet permet de scraper des articles depuis un site web, de les stocker dans une base de données MongoDB et de les afficher via une interface web avec des filtres.

## Prérequis

Avant de lancer le projet, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- **Python 3.8+**
- **Node.js** et **npm**
- **MongoDB** (en cours d'exécution sur `localhost:27017`)

## Installation

### 1. Cloner le dépôt

Clonez le dépôt sur votre machine locale :

```bash
git clone https://github.com/DamienLortieThibaut/TP_BeautifulSoup4.git
cd TP_BeautifulSoup4
```
### 2. Installer les dépendances Python

Accédez au dossier contenant le back-end et installez les dépendances Python :

```bash
pip install -r requirements.txt
```

### 3. Installer les dépendances du front

Accédez au dossier contenant le front-end React et installez les dépendances npm :

```bash
cd frontend
npm install
```

## Configuration 

### 1. MongoDB

Assurez-vous que MongoDB est en cours d'exécution sur `localhost:27017`. Une base de données nommée `app_articles_scrapping` sera utilisée pour stocker les articles. Si MongoDB n'est pas encore configuré, vous pouvez le démarrer avec la commande suivante (selon votre système d'exploitation) :

```bash
mongod
```

### 2. Variables d'environnement

Aucune configuration spécifique n'est nécessaire.

## Lancer le projet 

### 1. Lancer le back Flask

Depuis le dossier `TP_BeautifulSoup4`, exécutez le script Flask pour démarrer le serv back:

```bash
python app.py
```

Le serveur Flask sera accessible à l'adresse suivante : `http://127.0.0.1:5000`.

### 2. Lancer le script de scraping
Pour scraper les articles et les insérer dans MongoDB, exécutez le script scrap.py.

Ce script récupérera les articles des catégories spécifiées et les insérera dans la base de données MongoDB.

### 3. Lancer le front-end React
Depuis le dossier frontend, démarrez l'application React pour afficher les articles :

```bash
npm start
```

Le front-end sera accessible à l'adresse suivante : `http://localhost:3000`. Enjoy 😎👌🤙
