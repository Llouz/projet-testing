import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const normalizeStatut = (s) => {
  if (!s) return 'unknown';
  const lower = s.toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // enlève accents
  if (lower === 'en_attente' || lower === 'en attente') return 'en_attente';
  if (['acceptee', 'acceptée', 'valide', 'validee', 'validée'].includes(lower)) return 'acceptee';
  if (['rejette', 'rejete', 'rejetee', 'rejetée', 'refuse', 'refusee', 'refusée'].includes(lower)) return 'rejetee';
  return 'unknown';
};

const DemandesMedicaments = () => {
  const [demandes, setDemandes] = useState([]);
  const [error, setError] = useState('');
  const [loadingIds, setLoadingIds] = useState(new Set());

  const fetchDemandes = () => {
    setError('');
    api.get('/admin/demandes-medicaments')
      .then(res => {
        setDemandes(res.data);
      })
      .catch(() => setError("Erreur lors du chargement des demandes."));
  };

  const doAction = async (id, action) => {
    setLoadingIds(prev => new Set(prev).add(id));
    try {
      await api.post(`/admin/demandes-medicaments/${id}/${action}`);
      fetchDemandes();
    } catch (e) {
      setError(`Erreur lors de la tentative de ${action === 'valider' ? 'validation' : 'refus'}.`);
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
      <h3 style={{ marginBottom: 12 }}>Demandes de médicaments</h3>
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
          aria-label="Demandes de médicaments"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID</th>
              <th style={{ padding: '10px 12px' }}>Nom</th>
              <th style={{ padding: '10px 12px' }}>Quantité</th>
              <th style={{ padding: '10px 12px' }}>Expiration</th>
              <th style={{ padding: '10px 12px' }}>Statut</th>
              <th style={{ padding: '10px 12px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {demandes.map(d => {
              const statut = normalizeStatut(d.statut);
              return (
                <tr key={d.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '8px 12px' }}>{d.id}</td>
                  <td style={{ padding: '8px 12px' }}>{d.nom}</td>
                  <td style={{ padding: '8px 12px' }}>{d.quantite}</td>
                  <td style={{ padding: '8px 12px' }}>{d.date_expiration}</td>
                  <td style={{ padding: '8px 12px' }}>
                    {statut === 'en_attente' ? (
                      <span style={{
                        padding: '4px 8px',
                        background: '#fff3cd',
                        borderRadius: 4,
                        fontSize: 12,
                      }}>En attente</span>
                    ) : statut === 'acceptee' ? (
                      <span style={{
                        padding: '4px 8px',
                        background: '#d4edda',
                        borderRadius: 4,
                        fontSize: 12,
                      }}>Acceptée</span>
                    ) : statut === 'rejetee' ? (
                      <span style={{
                        padding: '4px 8px',
                        background: '#f8d7da',
                        borderRadius: 4,
                        fontSize: 12,
                      }}>Rejetée</span>
                    ) : (
                      <span style={{
                        padding: '4px 8px',
                        background: '#e2e3e5',
                        borderRadius: 4,
                        fontSize: 12,
                      }}>Inconnu</span>
                    )}
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    {statut === 'en_attente' ? (
                      <>
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
                      </>
                    ) : (
                      <em style={{ color: '#555', fontSize: 12 }}>—</em>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DemandesMedicaments;
