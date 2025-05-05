from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['app_articles_scrapping']
collection = db['articles']

@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        # Récupérer les paramètres de requête
        category = request.args.get('category')
        tag = request.args.get('tag')
        author = request.args.get('author')
        title_substring = request.args.get('title')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Construire la requête MongoDB
        query = {}
        if category:
            query['category'] = category
        if tag:
            query['tag'] = tag
        if author:
            query['firstname_author'] = {'$regex': author, '$options': 'i'}
        if title_substring:
            query['title'] = {'$regex': title_substring, '$options': 'i'}
        if start_date or end_date:
            query['publication_date'] = {}
            if start_date:
                query['publication_date']['$gte'] = datetime.fromisoformat(start_date)
            if end_date:
                query['publication_date']['$lte'] = datetime.fromisoformat(end_date)

        # Pagination
        skip = (page - 1) * limit
        articles_cursor = collection.find(query).skip(skip).limit(limit)
        articles = list(articles_cursor)

        # Formater les articles pour le JSON
        for article in articles:
            article['_id'] = str(article['_id'])

        return jsonify({
            'success': True,
            'data': articles,
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)