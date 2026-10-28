import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const badgeStyle = {
  padding: '4px 10px',
  borderRadius: 6,
  fontSize: 12,
  display: 'inline-block',
};

const MesLivraisons = () => {
  const [livraisons, setLivraisons] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [updatingIds, setUpdatingIds] = useState(new Set());
  const [message, setMessage] = useState('');

  const fetchLivraisons = async () => {
    try {
      const res = await api.get('/livreur/mes-livraisons');
      setLivraisons(res.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des livraisons.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLivraisons();
  }, []);

  const renderBadgeEtat = (etat) => {
    const lower = (etat || '').toString().toLowerCase();
    if (lower === 'en_cours' || lower === 'encours') {
      return <span style={{ ...badgeStyle, background: '#d1ecf1', color: '#0c5460' }}>En cours</span>;
    }
    if (lower === 'livree' || lower === 'livrée') {
      return <span style={{ ...badgeStyle, background: '#d4edda', color: '#155724' }}>Livrée</span>;
    }
    return <span style={{ ...badgeStyle, background: '#e2e3e5', color: '#6c757d' }}>{etat || 'Inconnu'}</span>;
  };

  const marquerLivree = async (id) => {
    setUpdatingIds(prev => new Set(prev).add(id));
    try {
      await api.put(`/livreur/livraisons/${id}/etat`, null, {
        params: { nouvel_etat: 'livree' },
      });
      setMessage("Livraison marquée comme livrée.");
      await fetchLivraisons();
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la mise à jour de l'état.");
    } finally {
      setUpdatingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>Mes livraisons</h3>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && livraisons.length === 0 && <p>Aucune livraison trouvée.</p>}

      {!loading && livraisons.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: 14,
              minWidth: 500,
            }}
            aria-label="Mes livraisons"
          >
            <thead>
              <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>ID Commande</th>
                <th style={{ padding: '10px 12px' }}>État</th>
                <th style={{ padding: '10px 12px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {livraisons.map((l) => (
                <tr key={l.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '8px 12px' }}>{l.commande_id}</td>
                  <td style={{ padding: '8px 12px' }}>{renderBadgeEtat(l.etat)}</td>
                  <td style={{ padding: '8px 12px' }}>
                    {['livree', 'livrée'].includes((l.etat || '').toString().toLowerCase()) ? (
                      <em style={{ color: '#555', fontSize: 12 }}>—</em>
                    ) : (
                      <button
                        onClick={() => marquerLivree(l.id)}
                        disabled={updatingIds.has(l.id)}
                        style={{
                          padding: '6px 14px',
                          borderRadius: 4,
                          border: '1px solid #28a745',
                          background: '#28a745',
                          color: '#fff',
                          cursor: updatingIds.has(l.id) ? 'not-allowed' : 'pointer',
                          fontSize: 12,
                        }}
                      >
                        {updatingIds.has(l.id) ? '...' : 'Livrée'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <style>{`
            div::-webkit-scrollbar {
              height: 6px;
            }
            div::-webkit-scrollbar-track {
              background: #f1f1f1;
            }
            div::-webkit-scrollbar-thumb {
              background: #888;
              border-radius: 3px;
            }
            div::-webkit-scrollbar-thumb:hover {
              background: #555;
            }
          `}</style>
        </div>
      )}
    </div>
  );
};

export default MesLivraisons;
