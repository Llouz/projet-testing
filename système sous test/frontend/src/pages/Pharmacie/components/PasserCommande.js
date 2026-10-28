import React, { useState } from 'react';

const PasserCommande = () => {
  const [medicament_id, setMedicamentId] = useState('');
  const [quantite, setQuantite] = useState('');
  const [distributeur_id, setDistributeurId] = useState('');
  const [message, setMessage] = useState('');

  const handleCommande = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    const res = await fetch('http://localhost:8000/pharmacie/commandes', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ medicament_id, quantite, distributeur_id })
    });

    const data = await res.json();
    if (res.ok) {
      setMessage('Commande effectuée avec succès');
    } else {
      setMessage(data.detail || 'Erreur');
    }
  };

  return (
    <div>
      <h2>Passer une commande</h2>
      <form onSubmit={handleCommande}>
        <input type="number" placeholder="ID Médicament" value={medicament_id} onChange={e => setMedicamentId(e.target.value)} required />
        <input type="number" placeholder="Quantité" value={quantite} onChange={e => setQuantite(e.target.value)} required />
        <input type="number" placeholder="ID Distributeur" value={distributeur_id} onChange={e => setDistributeurId(e.target.value)} required />
        <button type="submit">Commander</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default PasserCommande;
