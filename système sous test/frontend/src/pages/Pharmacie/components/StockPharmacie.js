import React, { useEffect, useState } from 'react';

const StockPharmacie = () => {
  const [stock, setStock] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('http://localhost:8000/pharmacie/stock', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => setStock(data));
  }, []);

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontFamily: 'Arial, sans-serif',
  };

  const thStyle = {
    backgroundColor: '#0074c2',
    color: 'white',
    padding: '12px',
    textAlign: 'left',
  };

  const tdStyle = {
    padding: '12px',
    borderBottom: '1px solid #ddd',
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Mon Stock</h2>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Nom</th>
            <th style={thStyle}>Quantité</th>
          </tr>
        </thead>
        <tbody>
          {stock.map((item) => (
            <tr key={item.id}>
              <td style={tdStyle}>{item.nom_medicament}</td>
              <td style={tdStyle}>{item.quantite}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockPharmacie;
