import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const MedicamentsCentrale = () => {
  const [medicaments, setMedicaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quantites, setQuantites] = useState({});
  const [messages, setMessages] = useState({});

  const fetchMedicaments = async () => {
    try {
      const response = await api.get('/distributeur/stock-centrale');
      setMedicaments(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError("Erreur lors du chargement des médicaments de la centrale.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMedicaments();
  }, []);

  const handleChangeQuantite = (id, value) => {
    setQuantites((prev) => ({
      ...prev,
      [id]: value
    }));
  };

  const handleCommander = async (id) => {
    const quantite = parseInt(quantites[id]);
    if (isNaN(quantite) || quantite <= 0) {
      setMessages((prev) => ({
        ...prev,
        [id]: '❌ Quantité invalide'
      }));
      return;
    }

    try {
      await api.post('/distributeur/commandes-stock', {
        medicament_id: id,
        quantite: quantite,
      });

      setMessages((prev) => ({
        ...prev,
        [id]: '✅ Commande envoyée'
      }));

      // Optionnel : reset champ quantité
      setQuantites((prev) => ({
        ...prev,
        [id]: ''
      }));
    } catch (err) {
      console.error(err);
      setMessages((prev) => ({
        ...prev,
        [id]: "❌ Erreur lors de l'envoi"
      }));
    }
  };

  return (
    <div>
      <h3>Médicaments disponibles à la centrale</h3>

      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && medicaments.length === 0 && (
        <p>Aucun médicament disponible.</p>
      )}

      {!loading && medicaments.length > 0 && (
        <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>ID Médicament</th>
              <th>Nom</th>
              <th>Quantité à commander</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {medicaments.map((m) => (
              <tr key={m.id}>
                <td>{m.id}</td>
                <td>{m.nom}</td>
                <td>
                  <input
                    type="number"
                    min="1"
                    value={quantites[m.id] || ''}
                    onChange={(e) => handleChangeQuantite(m.id, e.target.value)}
                    style={{ width: '80px' }}
                  />
                </td>
                <td>
                  <button onClick={() => handleCommander(m.id)}>Commander</button>
                  {messages[m.id] && (
                    <div style={{ fontSize: '12px', marginTop: '4px' }}>
                      {messages[m.id]}
                    </div>
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

export default MedicamentsCentrale;
