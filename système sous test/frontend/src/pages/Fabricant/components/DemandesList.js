import React, { useState } from 'react';

const normalizeStatut = (s) => {
  if (!s) return 'unknown';
  const lower = s.toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  if (lower === 'en_attente' || lower === 'en attente') return 'en_attente';
  if (['acceptee', 'acceptée', 'valide', 'validée'].includes(lower)) return 'acceptee';
  if (['rejette', 'rejetee', 'rejetée', 'refuse', 'refusée'].includes(lower)) return 'rejetee';
  return 'unknown';
};

const DemandesList = ({ demandes, onRefresh }) => {
  const [error, setError] = useState('');
  const [deletingIds, setDeletingIds] = useState(new Set());
  const token = localStorage.getItem('token');

  const supprimerDemande = async (id) => {
    const confirmDelete = window.confirm("Supprimer cette demande ?");
    if (!confirmDelete) return;

    setError('');
    setDeletingIds(prev => new Set(prev).add(id));
    try {
      const res = await fetch(
        `${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}/fabricant/demandes-medicaments/${id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (res.ok) {
        alert("Demande supprimée.");
        onRefresh();
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Erreur lors de la suppression.");
      }
    } catch (e) {
      setError("Erreur réseau.");
    } finally {
      setDeletingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>Mes demandes</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {demandes.length === 0 ? (
        <p>Aucune demande.</p>
      ) : (
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14,
            minWidth: 600,
          }}
          aria-label="Liste des demandes"
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
                    {statut === 'en_attente' && (
                      <span style={{ padding: '4px 8px', background: '#fff3cd', borderRadius: 4, fontSize: 12 }}>
                        En attente
                      </span>
                    )}
                    {statut === 'acceptee' && (
                      <span style={{ padding: '4px 8px', background: '#d4edda', borderRadius: 4, fontSize: 12 }}>
                        Acceptée
                      </span>
                    )}
                    {statut === 'rejetee' && (
                      <span style={{ padding: '4px 8px', background: '#f8d7da', borderRadius: 4, fontSize: 12 }}>
                        Rejetée
                      </span>
                    )}
                    {statut === 'unknown' && (
                      <span style={{ padding: '4px 8px', background: '#e2e3e5', borderRadius: 4, fontSize: 12 }}>
                        Inconnu
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    {statut === 'en_attente' ? (
                      <button
                        onClick={() => supprimerDemande(d.id)}
                        disabled={deletingIds.has(d.id)}
                        style={{
                          padding: '6px 12px',
                          borderRadius: 4,
                          border: '1px solid #dc3545',
                          background: '#dc3545',
                          color: '#fff',
                          cursor: deletingIds.has(d.id) ? 'not-allowed' : 'pointer',
                          fontSize: 12,
                        }}
                      >
                        {deletingIds.has(d.id) ? '…' : 'Supprimer'}
                      </button>
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

export default DemandesList;
