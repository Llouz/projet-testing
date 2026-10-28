import React, { useEffect, useState } from 'react';
import api from '../../../utils/api'; // Assure-toi que ce fichier ajoute automatiquement le token JWT

const ListeLivreurs = () => {
  const [livreurs, setLivreurs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erreur, setErreur] = useState('');

  useEffect(() => {
    const fetchLivreurs = async () => {
      try {
        const response = await api.get('/distributeur/mes-livreurs');
        setLivreurs(response.data);
      } catch (err) {
        console.error(err);
        setErreur("Erreur lors du chargement des livreurs.");
      } finally {
        setLoading(false);
      }
    };

    fetchLivreurs();
  }, []);

  return (
    <div>
      <h2>Liste de vos livreurs</h2>

      {loading && <p>Chargement...</p>}
      {erreur && <p style={{ color: 'red' }}>{erreur}</p>}

      {!loading && livreurs.length === 0 && <p>Aucun livreur enregistré.</p>}

      {!loading && livreurs.length > 0 && (
        <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nom</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {livreurs.map((livreur) => (
              <tr key={livreur.id}>
                <td>{livreur.id}</td>
                <td>{livreur.nom}</td>
                <td>{livreur.email}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ListeLivreurs;
