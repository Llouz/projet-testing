import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const StockDistributeur = () => {
  const [stock, setStock] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState({});

  useEffect(() => {
    api.get('/distributeur/stock')
      .then(res => {
        const stockAvecPrixEditable = res.data.map(item => ({
          ...item,
          nouveauPrix: item.prix_unitaire,
        }));
        setStock(stockAvecPrixEditable);
        setLoading(false);
      })
      .catch(err => {
        console.error('Erreur lors du chargement du stock :', err);
        setError('Erreur lors du chargement du stock');
        setLoading(false);
      });
  }, []);

  const handleChangePrix = (index, value) => {
    const updatedStock = [...stock];
    updatedStock[index].nouveauPrix = value;
    setStock(updatedStock);
  };

  const handleUpdatePrix = async (index) => {
    const medicament = stock[index];
    try {
      const nouveauPrix = parseFloat(medicament.nouveauPrix);
      await api.put('/distributeur/stock/prix', {
        medicament_id: medicament.medicament_id,
        prix_unitaire: nouveauPrix,
      });

      // mise à jour immédiate du prix affiché
      const updatedStock = [...stock];
      updatedStock[index].prix_unitaire = nouveauPrix;
      setStock(updatedStock);

      const updatedMessages = { ...messages };
      updatedMessages[medicament.medicament_id] = "✅ Prix mis à jour.";
      setMessages(updatedMessages);
    } catch (err) {
      console.error(err);
      const updatedMessages = { ...messages };
      updatedMessages[medicament.medicament_id] = "❌ Erreur lors de la mise à jour.";
      setMessages(updatedMessages);
    }
  };

  if (loading) return <p>Chargement du stock...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Stock des médicaments</h2>
      {stock.length === 0 ? (
        <p>Aucun stock disponible.</p>
      ) : (
      <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th>Nom</th>
            <th>Quantité</th>
            <th>Prix unitaire (DT)</th>
            <th>Modifier Prix</th>
          </tr>
        </thead>
        <tbody>
          {stock.map((item, index) => (
            <tr key={item.medicament_id}>
              <td>{item.nom}</td>
              <td>{item.quantite}</td>
              <td>{item.prix_unitaire} DT</td>
              <td>
                <input
                  type="number"
                  value={item.nouveauPrix}
                  onChange={(e) => handleChangePrix(index, e.target.value)}
                  style={{ width: '80px' }}
                />
                <button onClick={() => handleUpdatePrix(index)} style={{ marginLeft: '8px' }}>
                  Enregistrer
                </button>
                {messages[item.medicament_id] && (
                  <div style={{ fontSize: '12px', marginTop: '4px' }}>
                    {messages[item.medicament_id]}
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

export default StockDistributeur;
