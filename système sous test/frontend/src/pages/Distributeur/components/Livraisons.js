import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const badgeStyle = {
  padding: '4px 10px',
  borderRadius: 6,
  fontSize: 12,
  display: 'inline-block',
};

const Livraisons = () => {
  const [livraisons, setLivraisons] = useState([]);
  const [livreurs, setLivreurs] = useState([]);
  const [demandesLivreurs, setDemandesLivreurs] = useState([]);
  const [selectedLivreurs, setSelectedLivreurs] = useState({});
  const [loadingLivraisons, setLoadingLivraisons] = useState(true);
  const [loadingLivreurs, setLoadingLivreurs] = useState(true);
  const [loadingDemandes, setLoadingDemandes] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(new Set());
  const [actionLoadingDemande, setActionLoadingDemande] = useState(new Set());
  const [message, setMessage] = useState('');

  const fetchLivreurs = async () => {
    try {
      const res = await api.get('/distributeur/mes-livreurs');
      setLivreurs(res.data);
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des livreurs.");
    } finally {
      setLoadingLivreurs(false);
    }
  };

  const fetchLivraisons = async () => {
    try {
      const res = await api.get('/distributeur/livraisons');
      setLivraisons(res.data);
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des livraisons.");
    } finally {
      setLoadingLivraisons(false);
    }
  };

  const fetchDemandes = async () => {
    try {
      const res = await api.get('/distributeur/demandes-livreurs');
      setDemandesLivreurs(res.data);
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des demandes de livreurs.");
    } finally {
      setLoadingDemandes(false);
    }
  };

  useEffect(() => {
    fetchLivreurs();
    fetchLivraisons();
    fetchDemandes();
  }, []);

  const handleAttribution = async (livraisonId) => {
    const livreurId = selectedLivreurs[livraisonId];
    if (!livreurId) return;

    setActionLoading(prev => new Set(prev).add(livraisonId));
    try {
      await api.post('/distributeur/livraisons/attribuer-livreur', {
        livraison_id: livraisonId,
        livreur_id: parseInt(livreurId, 10),
      });

      setLivraisons(prev =>
        prev.map(l =>
          l.id === livraisonId
            ? { ...l, livreur_id: parseInt(livreurId, 10), etat: 'en_cours' }
            : l
        )
      );
      setError('');
    } catch (err) {
      console.error(err);
      setError("Échec de l’attribution du livreur.");
    } finally {
      setActionLoading(prev => {
        const next = new Set(prev);
        next.delete(livraisonId);
        return next;
      });
    }
  };

  const handleDemandeAction = async (id, action) => {
    setActionLoadingDemande(prev => new Set(prev).add(id));
    try {
      await api.post(`/distributeur/demandes-livreurs/${id}/${action}`);
      setMessage(`Demande ${action === 'valider' ? 'acceptée' : 'refusée'}.`);
      setDemandesLivreurs(prev => prev.filter(d => d.id !== id));
      setError('');
    } catch (err) {
      console.error(err);
      setError("Erreur lors du traitement de la demande.");
    } finally {
      setActionLoadingDemande(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const renderBadgeEtat = (etat) => {
    const lower = (etat || '').toString().toLowerCase();
    if (lower === 'en_attente') {
      return <span style={{ ...badgeStyle, background: '#fff3cd', color: '#856404' }}>En attente</span>;
    }
    if (lower === 'en_cours' || lower === 'encours') {
      return <span style={{ ...badgeStyle, background: '#d1ecf1', color: '#0c5460' }}>En cours</span>;
    }
    if (lower === 'terminee' || lower === 'terminée') {
      return <span style={{ ...badgeStyle, background: '#d4edda', color: '#155724' }}>Terminée</span>;
    }
    return <span style={{ ...badgeStyle, background: '#e2e3e5', color: '#6c757d' }}>Inconnue</span>;
  };

  return (
    <div style={{ display: 'flex', gap: 24, padding: 16, fontFamily: 'sans-serif' }}>
      {/* Colonne livraisons */}
      <div style={{ flex: 2, minWidth: 0 }}>
        <h3 style={{ marginBottom: 8 }}>Livraisons</h3>
        {message && <p style={{ color: 'green' }}>{message}</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {loadingLivraisons ? (
          <p>Chargement des livraisons...</p>
        ) : livraisons.length === 0 ? (
          <p>Aucune livraison enregistrée.</p>
        ) : (
          <div style={{ overflowX: 'auto', paddingBottom: 4, scrollbarWidth: 'thin' }}>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: 13,
                minWidth: 600,
              }}
              aria-label="Liste des livraisons"
            >
              <thead>
                <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
                  <th style={{ padding: '8px 10px' }}>ID Livraison</th>
                  <th style={{ padding: '8px 10px' }}>ID Commande</th>
                  <th style={{ padding: '8px 10px' }}>Livreur attribué</th>
                  <th style={{ padding: '8px 10px' }}>État</th>
                  <th style={{ padding: '8px 10px' }}>Attribuer</th>
                </tr>
              </thead>
              <tbody>
                {livraisons.map(l => (
                  <tr key={l.id} style={{ borderBottom: '1px solid #ddd' }}>
                    <td style={{ padding: '6px 10px', whiteSpace: 'nowrap' }}>{l.id}</td>
                    <td style={{ padding: '6px 10px', whiteSpace: 'nowrap' }}>{l.commande_id}</td>
                    <td style={{ padding: '6px 10px' }}>
                      {l.livreur_id !== null ? l.livreur_id : <em>Aucun</em>}
                    </td>
                    <td style={{ padding: '6px 10px' }}>{renderBadgeEtat(l.etat)}</td>
                    <td style={{ padding: '6px 10px', whiteSpace: 'nowrap' }}>
                      {l.etat === 'en_attente' ? (
                        <>
                          <select
                            value={selectedLivreurs[l.id] || ''}
                            onChange={(e) => setSelectedLivreurs(prev => ({ ...prev, [l.id]: e.target.value }))}
                            style={{
                              marginRight: 6,
                              padding: '5px 8px',
                              borderRadius: 4,
                              border: '1px solid #ccc',
                              fontSize: 12,
                            }}
                          >
                            <option value="">Choisir un livreur</option>
                            {livreurs.map(lv => (
                              <option key={lv.id} value={lv.id}>
                                {lv.nom} ({lv.id})
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={() => handleAttribution(l.id)}
                            disabled={actionLoading.has(l.id) || !selectedLivreurs[l.id]}
                            style={{
                              padding: '6px 12px',
                              borderRadius: 4,
                              border: '1px solid #007bff',
                              background: '#007bff',
                              color: '#fff',
                              cursor: actionLoading.has(l.id) ? 'not-allowed' : 'pointer',
                              fontSize: 12,
                            }}
                          >
                            {actionLoading.has(l.id) ? '…' : 'Attribuer'}
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

      <div style={{ flex: 1, minWidth: 260 }}>
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 8 }}>Liste de vos livreurs</h3>
          {loadingLivreurs ? (
            <p>Chargement des livreurs...</p>
          ) : livreurs.length === 0 ? (
            <p>Aucun livreur enregistré.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: 13,
                }}
                aria-label="Liste des livreurs"
              >
                <thead>
                  <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
                    <th style={{ padding: '8px 10px' }}>ID</th>
                    <th style={{ padding: '8px 10px' }}>Nom</th>
                    <th style={{ padding: '8px 10px' }}>Email</th>
                  </tr>
                </thead>
                <tbody>
                  {livreurs.map(lv => (
                    <tr key={lv.id} style={{ borderBottom: '1px solid #ddd' }}>
                      <td style={{ padding: '6px 10px', whiteSpace: 'nowrap' }}>{lv.id}</td>
                      <td style={{ padding: '6px 10px' }}>{lv.nom}</td>
                      <td style={{ padding: '6px 10px' }}>{lv.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div>
          <h4 style={{ marginBottom: 6 }}>Demandes des livreurs</h4>
          {loadingDemandes ? (
            <p style={{ margin: 0 }}>Chargement...</p>
          ) : demandesLivreurs.length === 0 ? (
            <p style={{ margin: 0 }}>Aucune demande en attente.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {demandesLivreurs.map(d => (
                <div
                  key={d.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '6px 10px',
                    border: '1px solid #ddd',
                    borderRadius: 6,
                    fontSize: 12,
                    background: '#fafafa',
                    gap: 8,
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div>
                      <strong>{d.nom}</strong> — <span style={{ color: '#555' }}>{d.email}</span>
                    </div>
                    <div style={{ marginTop: 2 }}>
                      <small>ID: {d.id}</small>
                    </div>
                  </div>
                  <div style={{ flexShrink: 0, display: 'flex', gap: 6 }}>
                    <button
                      onClick={() => handleDemandeAction(d.id, 'valider')}
                      disabled={actionLoadingDemande.has(d.id)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 4,
                        border: '1px solid #28a745',
                        background: '#28a745',
                        color: '#fff',
                        cursor: actionLoadingDemande.has(d.id) ? 'not-allowed' : 'pointer',
                        fontSize: 12,
                      }}
                    >
                      {actionLoadingDemande.has(d.id) ? '…' : 'Accepter'}
                    </button>
                    <button
                      onClick={() => handleDemandeAction(d.id, 'refuser')}
                      disabled={actionLoadingDemande.has(d.id)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 4,
                        border: '1px solid #dc3545',
                        background: '#fff',
                        color: '#dc3545',
                        cursor: actionLoadingDemande.has(d.id) ? 'not-allowed' : 'pointer',
                        fontSize: 12,
                      }}
                    >
                      {actionLoadingDemande.has(d.id) ? '…' : 'Refuser'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Livraisons;
