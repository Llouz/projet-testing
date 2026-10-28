import React, { useState } from 'react';
import api from '../../../utils/api';

const CommandesStock = () => {
  const [id, setId] = useState('');
  const [quantite, setQuantite] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!id || !quantite || isNaN(id) || isNaN(quantite)) {
      setError("Veuillez entrer un ID et une quantité valides.");
      return;
    }

    try {
      await api.post('/distributeur/commandes-stock', {
        medicament_id: parseInt(id),
        quantite: parseInt(quantite),
      });

      setMessage("Commande envoyée à la centrale.");
      setError('');
      setId('');
      setQuantite('');
    } catch (err) {
      console.error(err);
      setError("Une erreur est survenue lors de l'envoi de la commande.");
      setMessage('');
    }
  };

  return (
    <div>
      <h3>Commande de médicament vers la centrale</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="ID médicament"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />
        <input
          type="text"
          placeholder="Quantité"
          value={quantite}
          onChange={(e) => setQuantite(e.target.value)}
        />
        <button type="submit">Commander</button>
      </form>

      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default CommandesStock;
