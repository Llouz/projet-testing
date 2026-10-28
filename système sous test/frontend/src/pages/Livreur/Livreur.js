import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LivreurInfos from './components/LivreurInfos';
import MesLivraisons from './components/MesLivraisons';
import './Livreur.css';

const Livreur = () => {
  const [currentView, setCurrentView] = useState('infos');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  return (
    <div className="livreur-container">
      <h1>Espace Livreur</h1>
      <div className="livreur-nav">
        <button onClick={() => setCurrentView('infos')}>Mes Infos</button>
        <button onClick={() => setCurrentView('livraisons')}>Mes Livraisons</button>
        <button onClick={handleLogout}>Se déconnecter</button>
      </div>

      <div className="livreur-content">
        {currentView === 'infos' && <LivreurInfos />}
        {currentView === 'livraisons' && <MesLivraisons />}
      </div>
    </div>
  );
};

export default Livreur;
