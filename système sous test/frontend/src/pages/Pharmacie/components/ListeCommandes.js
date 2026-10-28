import React, { useEffect, useState } from 'react';

const ListeCommandes = () => {
  const [commandes, setCommandes] = useState([]);
  const [message, setMessage] = useState('');

  const fetchCommandes = () => {
    const token = localStorage.getItem('token');
    fetch('http://localhost:8000/pharmacie/commandes', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setCommandes(data));
  };

  useEffect(() => {
    fetchCommandes();
  }, []);

  const confirmerReception = async (id) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`http://localhost:8000/pharmacie/commandes/${id}/confirmer-reception`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await res.json();
    if (res.ok) {
      setMessage(`Commande ${id} confirmée`);
      fetchCommandes();
    } else {
      setMessage(data.detail || 'Erreur');
    }
  };

  // Filtrer les commandes : ne pas afficher celles avec statut "reçue"
  const commandesAffichees = commandes.filter(c => c.statut !== 'reçue');

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h2>Mes Commandes</h2>

      {message && <p style={{ color: 'green' }}>{message}</p>}

      {commandesAffichees.length === 0 ? (
        <p>Aucune commande à afficher.</p>
      ) : (
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14,
            minWidth: 600,
          }}
          aria-label="Liste des commandes"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID</th>
              <th style={{ padding: '10px 12px' }}>Médicament</th>
              <th style={{ padding: '10px 12px' }}>Quantité</th>
              <th style={{ padding: '10px 12px' }}>Statut</th>
              <th style={{ padding: '10px 12px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {commandesAffichees.map(c => (
              <tr key={c.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '8px 12px' }}>{c.id}</td>
                <td style={{ padding: '8px 12px' }}>{c.medicament_id}</td>
                <td style={{ padding: '8px 12px' }}>{c.quantite}</td>
                <td style={{ padding: '8px 12px' }}>{c.statut}</td>
                <td style={{ padding: '8px 12px' }}>
                  {c.statut === 'validée' && (
                    <button
                      onClick={() => confirmerReception(c.id)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 4,
                        border: '1px solid #28a745',
                        background: '#28a745',
                        color: '#fff',
                        fontSize: 12,
                        cursor: 'pointer',
                      }}
                    >
                      Confirmer réception
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ListeCommandes;
