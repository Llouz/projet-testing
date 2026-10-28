import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const DemandesStockDistributeur = () => {
  const [demandes, setDemandes] = useState([]);
  const [error, setError] = useState('');
  const [loadingIds, setLoadingIds] = useState(new Set());

  const fetchDemandes = () => {
    api.get('/admin/demandes-stock-distributeurs')
      .then(res => {
        setDemandes(res.data);
        setError('');
      })
      .catch(() => setError("Erreur lors du chargement."));
  };

  const doAction = async (id, action) => {
    setLoadingIds(prev => new Set(prev).add(id));
    try {
      await api.post(`/admin/demandes-stock-distributeurs/${id}/${action}`);
      fetchDemandes();
    } catch (err) {
      if (action === 'valider' && err.response && err.response.status === 400) {
        setError(err.response.data.detail);
      } else {
        setError(
          action === 'valider'
            ? "Erreur lors de la validation."
            : "Erreur lors du refus."
        );
      }
    } finally {
      setLoadingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  useEffect(() => {
    fetchDemandes();
  }, []);

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>Demandes de stock des distributeurs</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {demandes.length === 0 ? (
        <p>Aucune demande trouvée.</p>
      ) : (
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14,
            minWidth: 700,
          }}
          aria-label="Demandes de stock des distributeurs"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID</th>
              <th style={{ padding: '10px 12px' }}>Distributeur</th>
              <th style={{ padding: '10px 12px' }}>Médicament</th>
              <th style={{ padding: '10px 12px' }}>Quantité</th>
              <th style={{ padding: '10px 12px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {demandes.map(d => (
              <tr key={d.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '8px 12px' }}>{d.id}</td>
                <td style={{ padding: '8px 12px' }}>{d.nom_distributeur}</td>
                <td style={{ padding: '8px 12px' }}>
                  <strong>{d.nom_medicament}</strong>
                </td>
                <td style={{ padding: '8px 12px' }}>{d.quantite}</td>
                <td style={{ padding: '8px 12px' }}>
                  <button
                    onClick={() => doAction(d.id, 'valider')}
                    disabled={loadingIds.has(d.id)}
                    style={{
                      marginRight: 6,
                      padding: '6px 12px',
                      borderRadius: 4,
                      border: '1px solid #28a745',
                      background: '#28a745',
                      color: '#fff',
                      cursor: loadingIds.has(d.id) ? 'not-allowed' : 'pointer',
                      fontSize: 12,
                    }}
                  >
                    {loadingIds.has(d.id) ? '…' : 'Valider'}
                  </button>
                  <button
                    onClick={() => doAction(d.id, 'refuser')}
                    disabled={loadingIds.has(d.id)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 4,
                      border: '1px solid #dc3545',
                      background: '#dc3545',
                      color: '#fff',
                      cursor: loadingIds.has(d.id) ? 'not-allowed' : 'pointer',
                      fontSize: 12,
                    }}
                  >
                    {loadingIds.has(d.id) ? '…' : 'Refuser'}
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

export default DemandesStockDistributeur;
