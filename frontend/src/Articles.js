import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Articles = () => {
  const [articles, setArticles] = useState([]);
  const [category, setCategory] = useState('');
  const [tag, setTag] = useState('');
  const [author, setAuthor] = useState('');
  const [title, setTitle] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchArticles();
  }, [category, tag, author, title, startDate, endDate, page]);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:5000/articles', {
        params: {
          category,
          tag,
          author,
          title,
          start_date: startDate,
          end_date: endDate,
          page,
          limit,
        },
      });
      setArticles(response.data.data);
    } catch (error) {
      console.error('Erreur lors de la récupération des articles:', error);
    }
    setLoading(false);
  };

  const handleCategoryChange = (e) => setCategory(e.target.value);
  const handleTagChange = (e) => setTag(e.target.value);
  const handleAuthorChange = (e) => setAuthor(e.target.value);
  const handleTitleChange = (e) => setTitle(e.target.value);
  const handleStartDateChange = (e) => setStartDate(e.target.value);
  const handleEndDateChange = (e) => setEndDate(e.target.value);

  const handleNextPage = () => setPage((prevPage) => prevPage + 1);
  const handlePreviousPage = () => {
    if (page > 1) setPage((prevPage) => prevPage - 1);
  };

  return (
    <div>
      <h1>Articles</h1>

      {/* Filtres */}
      <div>
        <label>
          Catégorie :
          <input
            type="text"
            value={category}
            onChange={handleCategoryChange}
            placeholder="Ex: web"
          />
        </label>
        <label>
          Tag :
          <input
            type="text"
            value={tag}
            onChange={handleTagChange}
            placeholder="Ex: Culture web"
          />
        </label>
        <label>
          Auteur :
          <input
            type="text"
            value={author}
            onChange={handleAuthorChange}
            placeholder="Ex: Étienne"
          />
        </label>
        <label>
          Titre contient :
          <input
            type="text"
            value={title}
            onChange={handleTitleChange}
            placeholder="Ex: Skype"
          />
        </label>
        <label>
          Date de début :
          <input
            type="date"
            value={startDate}
            onChange={handleStartDateChange}
          />
        </label>
        <label>
          Date de fin :
          <input
            type="date"
            value={endDate}
            onChange={handleEndDateChange}
          />
        </label>
      </div>

      {/* Liste des articles */}
      {loading ? (
        <p>Chargement...</p>
      ) : (
        <ul>
          {articles.map((article) => (
            <li key={article._id}>
              {article ? (
                <>
                  <h2>{article.title}</h2>
                  <p>{article.summary}</p>
                  <img
                    src={article.thumbnail}
                    alt={article.title}
                    style={{ width: '200px' }}
                  />
                  <p>
                    Auteur : {article.firstname_author}{' '}
                    {article.lastname_author}
                  </p>
                  <p>Publié le : {new Date(article.publication_date).toLocaleString('fr')}</p>
                </>
              ) : (
                <p>Article mal formaté ou vide.</p>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Pagination */}
      <div>
        <button onClick={handlePreviousPage} disabled={page === 1}>
          Page précédente
        </button>
        <span>Page {page}</span>
        <button onClick={handleNextPage}>Page suivante</button>
      </div>
    </div>
  );
};

export default Articles;