import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
from tqdm import tqdm
import logging
from datetime import datetime

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['app_articles_scrapping']
collection = db['articles']

# Création d'un index unique sur le champ 'url' pour éviter les doublons
collection.create_index('url', unique=True)
logger.info("Connexion réussie à MongoDB et index créé sur le champ 'url'.")

# Configuration des constantes
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
BASE_URL = "https://www.blogdumoderateur.com/"
CATEGORIES = ["web", "marketing", "social", "tech"]
MAX_PAGES = 5

# Session HTTP persistante
session = requests.Session()
session.headers.update(HEADERS)

# Fonction utilitaire pour extraire du texte ou un attribut d'une balise
def get_text_or_none(tag, selector=None, attribute=None):
    if not tag:
        return None
    element = tag.find(selector) if selector else tag
    if attribute:
        return element[attribute] if element and attribute in element.attrs else None
    return element.get_text(strip=True) if element else None

# Récupérer les détails d'un article
def fetch_detail_article(url, tag=None):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        main_tag = soup.find('main')
        if not main_tag:
            logger.warning(f"Aucun tag <main> trouvé pour l'URL : {url}")
            return None

        article = main_tag.find('article')
        header = article.find('header', class_='entry-header article-header text-center') if article else None

        title = get_text_or_none(header, 'h1')
        thumbnail = get_text_or_none(header.find('figure', class_='article-hat-img').find('img'), None, 'data-lazy-src') or \
                    get_text_or_none(header.find('figure', class_='article-hat-img').find('img'), None, 'src')
        div_tag_summary = header.find('div', class_='article-hat t-quote pb-md-8 pb-5') if header else None
        summary = div_tag_summary.find('p').get_text(strip=True) if div_tag_summary else None
        publication_date = get_text_or_none(header.find('span', class_='posted-on').find('time'), None, 'datetime')
        if publication_date:
            publication_date = datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%S%z')
        author_tag = header.find('span', class_='byline').find('a') if header else None
        author_name = author_tag['title'] if author_tag and 'title' in author_tag.attrs else None
        firstname_author, lastname_author = (author_name.split(' ', 1) if author_name else (None, None))

        # Collecte des images
        images = []
        img_tags = article.find_all('img') if article else []
        for index, img in enumerate(img_tags):
            img_src = img.get('data-lazy-src') or img.get('src')
            alt_text = img.get('alt', '').strip()
            images.append({
                'order_of_appearance': index,
                'url': img_src,
                'alt_text': alt_text
            })

        return {
            'title': title,
            'tag': tag,
            'thumbnail': thumbnail,
            'summary': summary,
            'publication_date': publication_date,
            'firstname_author': firstname_author,
            'lastname_author': lastname_author,
            'images': images,
            'url': url 
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la récupération des détails de l'article : {e}")
        return None

# Récupérer les articles d'une catégorie
def fetch_articles(url, category):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        main_tag = soup.find('main')
        if not main_tag:
            logger.warning(f"Aucun tag <main> trouvé pour l'URL : {url}")
            return []

        articles_data = []
        articles = soup.find_all('article')
        for article in articles:
            meta_div = article.find('div', class_='entry-meta ms-md-5 pt-md-0 pt-3')
            if not meta_div:
                logger.warning("Aucun tag <div> trouvé pour l'article.")
                continue
            tag = meta_div.find('span', class_='favtag color-b').get_text(strip=True) if meta_div else None

            header = meta_div.find('header', class_='entry-header pt-1') if meta_div else None
            article_url = get_text_or_none(header.find('a'), None, 'href') if header else None

            # Vérifiez si l'article existe déjà dans la base de données
            if article_url and not collection.find_one({'url': article_url}):
                article_details = fetch_detail_article(article_url, tag)
                if article_details:
                    # Ajoutez la catégorie à l'article
                    article_details['category'] = category
                    articles_data.append(article_details)
            else:
                logger.info(f"Article déjà présent en base : {article_url}")
        return articles_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la récupération des articles : {e}")
        return []

# Récupérer le nombre maximum de pages pour une catégorie
def max_pages(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        main_tag = soup.find('main')
        if not main_tag:
            logger.warning(f"Aucun tag <main> trouvé pour l'URL : {url}")
            return 0

        pager_tag = main_tag.find('div', class_='col-xl-12 pager')
        last_page = get_text_or_none(pager_tag.find('span', class_='e-link last'), None, 'data-href')
        if last_page:
            match = re.search(r'cntr/(\d+)', last_page)
            return int(match.group(1)) if match else 0
        return 0
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la récupération du nombre de pages : {e}")
        return 0

# Script principal
for category in CATEGORIES:
    category_url = f"{BASE_URL}{category}/"
    max_page = min(max_pages(category_url), MAX_PAGES)
    articles = []

    for page in tqdm(range(1, max_page + 1), desc=f"Fetching {category}"):
        page_url = f"{category_url}page/{page}/" if page > 1 else category_url
        articles.extend(fetch_articles(page_url, category))

    # Ajout des articles dans MongoDB
    try:
        if articles:
            collection.insert_many(articles, ordered=False)
            logger.info(f"{len(articles)} articles insérés pour la catégorie '{category}'.")
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion dans MongoDB : {e}")

logger.info("Tous les articles ont été insérés dans MongoDB avec succès.")