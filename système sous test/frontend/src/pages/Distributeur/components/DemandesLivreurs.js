import React, { useEffect, useState } from 'react';
import api from '../../../utils/api'; // Utilise ton instance Axios déjà configurée

const DemandesLivreurs = () => {
  const [demandes, setDemandes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const fetchDemandes = async () => {
    try {
      const res = await api.get('/distributeur/demandes-livreurs');
      setDemandes(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des demandes.");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemandes();
  }, []);

  const handleAction = async (id, action) => {
    try {
      await api.post(`/distributeur/demandes-livreurs/${id}/${action}`);
      setMessage(`Demande ${action === 'valider' ? 'acceptée' : 'refusée'}.`);
      setDemandes((prev) => prev.filter((d) => d.id !== id)); // Supprime localement
    } catch (err) {
      console.error(err);
      setError("Erreur lors du traitement de la demande.");
    }
  };

  if (loading) return <p>Chargement des demandes...</p>;

  return (
    <div>
      <h3>Demandes des livreurs</h3>

      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {demandes.length === 0 ? (
        <p>Aucune demande en attente.</p>
      ) : (
        <ul>
          {demandes.map((demande) => (
            <li key={demande.id} style={{ marginBottom: '10px' }}>
              <strong>{demande.nom}</strong> — {demande.email}
              <br />
              <button onClick={() => handleAction(demande.id, 'valider')} style={{ marginRight: '5px' }}>
                Accepter
              </button>
              <button onClick={() => handleAction(demande.id, 'refuser')} style={{ color: 'red' }}>
                Refuser
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DemandesLivreurs;
