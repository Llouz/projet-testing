import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const CommandesPharmacies = () => {
  const [commandes, setCommandes] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loadingIds, setLoadingIds] = useState(new Set());

  const fetchCommandes = async () => {
    try {
      const res = await api.get('/distributeur/commandes-pharmacies');
      setCommandes(res.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des commandes.");
    }
  };

  useEffect(() => {
    fetchCommandes();
  }, []);

  const doAction = async (id, action) => {
    setLoadingIds(prev => new Set(prev).add(id));
    try {
      await api.post(`/distributeur/commandes-pharmacies/${id}/${action}`);
      setMessage(
        action === 'valider'
          ? "Commande validée avec succès."
          : "Commande refusée avec succès."
      );
      setError('');
      await fetchCommandes();
    } catch (err) {
      console.error(err);
      setError(
        action === 'valider'
          ? "Erreur lors de la validation."
          : "Erreur lors du refus."
      );
      setMessage('');
    } finally {
      setLoadingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>Commandes reçues des pharmacies</h3>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {commandes.length === 0 ? (
        <p>Aucune commande en attente.</p>
      ) : (
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14,
            minWidth: 600,
          }}
          aria-label="Commandes des pharmacies"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID</th>
              <th style={{ padding: '10px 12px' }}>Médicament</th>
              <th style={{ padding: '10px 12px' }}>Quantité</th>
              <th style={{ padding: '10px 12px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {commandes.map(c => (
              <tr key={c.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '8px 12px' }}>{c.id}</td>
                <td style={{ padding: '8px 12px' }}>{c.nom_medicament}</td>
                <td style={{ padding: '8px 12px' }}>{c.quantite}</td>
                <td style={{ padding: '8px 12px' }}>
                  <button
                    onClick={() => doAction(c.id, 'valider')}
                    disabled={loadingIds.has(c.id)}
                    style={{
                      marginRight: 6,
                      padding: '6px 12px',
                      borderRadius: 4,
                      border: '1px solid #28a745',
                      background: '#28a745',
                      color: '#fff',
                      cursor: loadingIds.has(c.id) ? 'not-allowed' : 'pointer',
                      fontSize: 12,
                    }}
                  >
                    {loadingIds.has(c.id) ? '…' : 'Valider'}
                  </button>
                  <button
                    onClick={() => doAction(c.id, 'refuser')}
                    disabled={loadingIds.has(c.id)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 4,
                      border: '1px solid #dc3545',
                      background: '#dc3545',
                      color: '#fff',
                      cursor: loadingIds.has(c.id) ? 'not-allowed' : 'pointer',
                      fontSize: 12,
                    }}
                  >
                    {loadingIds.has(c.id) ? '…' : 'Refuser'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default CommandesPharmacies;
