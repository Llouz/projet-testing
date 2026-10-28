import React, { useState } from 'react';

const NouvelleDemandeForm = ({ onSuccess }) => {
  const [nom, setNom] = useState('');
  const [description, setDescription] = useState('');
  const [dateExp, setDateExp] = useState('');
  const [quantite, setQuantite] = useState('');
  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch('http://localhost:8000/fabricant/demandes-medicaments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        nom,
        description,
        date_expiration: dateExp,
        quantite: parseInt(quantite),
      }),
    });

    if (res.ok) {
      alert("Demande soumise !");
      setNom('');
      setDescription('');
      setDateExp('');
      setQuantite('');
      onSuccess();
    } else {
      alert("Erreur lors de la soumission.");
    }
  };

  return (
    <div>
      <h3>Soumettre une nouvelle demande</h3>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Nom" value={nom} onChange={e => setNom(e.target.value)} required />
        <input type="text" placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} required />
        <input type="date" value={dateExp} onChange={e => setDateExp(e.target.value)} required />
        <input type="number" placeholder="Quantité à fournir" value={quantite} onChange={e => setQuantite(e.target.value)} required />
        <button type="submit">Envoyer</button>
      </form>
    </div>
  );
};

export default NouvelleDemandeForm;
