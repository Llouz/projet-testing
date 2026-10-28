import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

function InfosDistributeur() {
  const [infos, setInfos] = useState(null);

  useEffect(() => {
    api.get('/distributeur/infos')
      .then(res => setInfos(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="border p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-2">Informations</h2>
      {infos ? (
        <ul>
          <li><strong>Nom :</strong> {infos.nom}</li>
          <li><strong>Email :</strong> {infos.email}</li>
        </ul>
      ) : (
        <p>Chargement...</p>
      )}
    </div>
  );
}

export default InfosDistributeur;
