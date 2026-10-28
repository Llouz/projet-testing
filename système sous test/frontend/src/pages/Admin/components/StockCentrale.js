import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const StockCentrale = () => {
  const [stock, setStock] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/admin/stock')
      .then(res => setStock(res.data))
      .catch(() => setError("Erreur lors du chargement du stock."));
  }, []);

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>Stock de la pharmacie centrale</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {stock.length === 0 ? (
        <p>Aucun stock disponible.</p>
      ) : (
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 14,
            minWidth: 600,
          }}
          aria-label="Stock de la pharmacie centrale"
        >
          <thead>
            <tr style={{ backgroundColor: '#1f78c1', color: 'white', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px' }}>ID Médicament</th>
              <th style={{ padding: '10px 12px' }}>Nom du médicament</th>
              <th style={{ padding: '10px 12px' }}>Quantité</th>
            </tr>
          </thead>
          <tbody>
            {stock.map((s, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={{ padding: '8px 12px' }}>{s.medicament_id}</td>
                <td style={{ padding: '8px 12px' }}>{s.nom_medicament}</td>
                <td style={{ padding: '8px 12px' }}>{s.quantite}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default StockCentrale;
