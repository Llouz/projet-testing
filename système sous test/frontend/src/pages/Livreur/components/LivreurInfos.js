import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const LivreurInfos = () => {
  const [infos, setInfos] = useState(null);
  const [error, setError] = useState('');

  const fetchInfos = async () => {
    try {
      const res = await api.get('/livreur/infos');
      setInfos(res.data);
      setError('');
    } catch (err) {
      setError("Erreur lors du chargement des informations.");
    }
  };

  useEffect(() => {
    fetchInfos();
  }, []);

  return (
    <div>
      <h3>Mes Informations</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {infos && (
        <ul>
          <li><strong>ID :</strong> {infos.id}</li>
          <li><strong>Nom :</strong> {infos.nom}</li>
          <li><strong>Email :</strong> {infos.email}</li>
        </ul>
      )}
    </div>
  );
};

export default LivreurInfos;
