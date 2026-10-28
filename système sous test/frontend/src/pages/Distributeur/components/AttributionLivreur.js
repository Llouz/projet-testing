import React, { useState } from 'react';
import api from '../../../utils/api';

const AttributionLivreur = () => {
  const [livraisonId, setLivraisonId] = useState('');
  const [livreurId, setLivreurId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!livraisonId || !livreurId) {
      setError("Veuillez remplir les deux champs.");
      setMessage('');
      return;
    }

    try {
      await api.post('/distributeur/livraisons/attribuer-livreur', {
        livraison_id: parseInt(livraisonId),
        livreur_id: parseInt(livreurId),
      });
      setMessage("Livreur attribué avec succès.");
      setError('');
      setLivraisonId('');
      setLivreurId('');
    } catch (err) {
      console.error(err);
      setError("Échec de l’attribution du livreur.");
      setMessage('');
    }
  };

  return (
    <div>
      <h3>Attribuer un livreur à une livraison</h3>

      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="ID de la livraison"
          value={livraisonId}
          onChange={(e) => setLivraisonId(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="ID du livreur"
          value={livreurId}
          onChange={(e) => setLivreurId(e.target.value)}
          required
        />
        <button type="submit" style={{ marginTop: '10px' }}>Attribuer</button>
      </form>
    </div>
  );
};

export default AttributionLivreur;
