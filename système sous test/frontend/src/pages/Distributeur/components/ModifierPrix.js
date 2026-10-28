import React, { useState } from 'react';
import api from '../../../utils/api';

const ModifierPrix = () => {
  const [id, setId] = useState('');
  const [prix, setPrix] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!id || !prix || isNaN(id) || isNaN(prix)) {
      setError("Veuillez entrer un ID et un prix valides.");
      return;
    }

    try {
      await api.put('/distributeur/stock/prix', {
        medicament_id: parseInt(id),
        prix_unitaire: parseFloat(prix),
      });

      setMessage("Prix mis à jour avec succès.");
      setError('');
      setId('');
      setPrix('');
    } catch (err) {
      console.error(err);
      setError("Une erreur est survenue lors de la mise à jour du prix.");
      setMessage('');
    }
  };

  return (
    <div>
      <h3>Modifier le prix d’un médicament</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="ID médicament"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />
        <input
          type="text"
          placeholder="Nouveau prix"
          value={prix}
          onChange={(e) => setPrix(e.target.value)}
        />
        <button type="submit">Modifier</button>
      </form>

      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ModifierPrix;
