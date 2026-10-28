import React, { useEffect, useState } from 'react';

const CatalogueDistributeurs = () => {
  const [catalogue, setCatalogue] = useState([]);
  const [quantites, setQuantites] = useState({});
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('http://localhost:8000/pharmacie/catalogues', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setCatalogue(data));
  }, []);

  const handleQuantiteChange = (id, value) => {
    setQuantites(prev => ({ ...prev, [id]: value }));
  };

  const handleCommande = async (item) => {
    const quantite = quantites[item.id];
    if (!quantite || quantite <= 0) {
      alert("Veuillez saisir une quantité valide.");
      return;
    }

    const token = localStorage.getItem('token');
    const res = await fetch('http://localhost:8000/pharmacie/commandes', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        medicament_id: item.medicament_id,
        quantite: parseInt(quantite),
        distributeur_id: item.distributeur_id
      })
    });

    const data = await res.json();
    if (res.ok) {
      setMessage(`✅ Commande réussie pour ${item.nom_medicament}`);
      setQuantites(prev => ({ ...prev, [item.id]: '' }));
    } else {
      setMessage(`❌ Erreur : ${data.detail || 'Commande échouée'}`);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Catalogue des Distributeurs</h2>
      {message && <p>{message}</p>}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'Arial, sans-serif' }}>
        <thead>
          <tr style={{ backgroundColor: '#0074c2', color: 'white' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Médicament</th>
            <th style={{ padding: '12px', textAlign: 'left' }}>Prix (dt)</th>
            <th style={{ padding: '12px', textAlign: 'left' }}>Quantité dispo</th>
            <th style={{ padding: '12px', textAlign: 'left' }}>Distributeur ID</th>
            <th style={{ padding: '12px', textAlign: 'left' }}>Commander</th>
          </tr>
        </thead>
        <tbody>
          {catalogue.map(item => (
            <tr key={item.id}>
              <td style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>{item.nom_medicament}</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>{item.prix_unitaire}</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>{item.quantite}</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>{item.distributeur_id}</td>
              <td style={{ padding: '12px', borderBottom: '1px solid #ddd' }}>
                <input
                  type="number"
                  min="1"
                  value={quantites[item.id] || ''}
                  onChange={e => handleQuantiteChange(item.id, e.target.value)}
                  placeholder="Qté"
                  style={{ width: '60px', marginRight: '5px' }}
                />
                <button onClick={() => handleCommande(item)} style={{ backgroundColor: '#28a745', color: 'white', border: 'none', padding: '6px 10px', borderRadius: '4px', cursor: 'pointer' }}>
                  Commander
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CatalogueDistributeurs;
