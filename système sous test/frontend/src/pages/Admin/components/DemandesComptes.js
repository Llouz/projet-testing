import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const DemandesComptes = () => {
  const [demandes, setDemandes] = useState([]);
  const [error, setError] = useState('');
  const [loadingIds, setLoadingIds] = useState(new Set()); // pour désactiver les boutons pendant l'action

  const fetchDemandes = () => {
    setError('');
    api.get('/admin/demandes-comptes')
      .then(res => setDemandes(res.data))
      .catch(() => setError("Erreur lors du chargement des demandes."));
  };

  const doAction = async (id, action) => {
    setLoadingIds(prev => new Set(prev).add(id));
    try {
      await api.post(`/admin/demandes-comptes/${id}/${action}`);
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
      <h3 style={{ marginBottom: 12 }}>Demandes de création de compte</h3>
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
          aria-label="Demandes de création de compte"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID</th>
              <th style={{ padding: '10px 12px' }}>Nom</th>
              <th style={{ padding: '10px 12px' }}>Email</th>
              <th style={{ padding: '10px 12px' }}>Type</th>
              <th style={{ padding: '10px 12px' }}>Statut</th>
              <th style={{ padding: '10px 12px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {demandes.map(d => (
              <tr key={d.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '8px 12px' }}>{d.id}</td>
                <td style={{ padding: '8px 12px' }}>{d.nom}</td>
                <td style={{ padding: '8px 12px' }}>{d.email}</td>
                <td style={{ padding: '8px 12px', textTransform: 'capitalize' }}>{d.type_utilisateur}</td>
                <td style={{ padding: '8px 12px' }}>
                  {d.statut === 'en_attente' ? (
                    <span style={{
                      padding: '4px 8px',
                      background: '#fff3cd',
                      borderRadius: 4,
                      fontSize: 12,
                    }}>En attente</span>
                  ) : d.statut === 'acceptée' ? (
                    <span style={{
                      padding: '4px 8px',
                      background: '#d4edda',
                      borderRadius: 4,
                      fontSize: 12,
                    }}>Validée</span>
                  ) : (
                    <span style={{
                      padding: '4px 8px',
                      background: '#f8d7da',
                      borderRadius: 4,
                      fontSize: 12,
                    }}>Refusée</span>
                  )}
                </td>
                <td style={{ padding: '8px 12px' }}>
                  {d.statut === 'en_attente' ? (
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
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DemandesComptes;
