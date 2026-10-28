import React from 'react';

const InfosFabricant = ({ infos }) => (
  <div>
    <h3>Mes Informations</h3>
    <p><strong>Nom :</strong> {infos.nom}</p>
    <p><strong>Email :</strong> {infos.email}</p>
  </div>
);

export default InfosFabricant;  
