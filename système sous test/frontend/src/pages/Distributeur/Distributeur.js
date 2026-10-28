// src/pages/Distributeur/Distributeur.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InfosDistributeur from './components/InfosDistributeur';
import StockDistributeur from './components/StockDistributeur';
import MedicamentsCentrale from './components/MedicamentsCentrale';
import CommandesPharmacies from './components/CommandesPharmacies';
import Livraisons from './components/Livraisons';
import './Distributeur.css'; 

const Distributeur = () => {
  const [currentView, setCurrentView] = useState('infos');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  return (
    <div className="distributeur-container">
      <h1>Espace Distributeur</h1>

      <nav>
        <button onClick={() => setCurrentView('infos')}>Mes Infos</button>
        <button onClick={() => setCurrentView('stock')}>Mon Stock</button>
        <button onClick={() => setCurrentView('centrale')}>Commander à la Centrale</button>
        <button onClick={() => setCurrentView('pharmacies')}>Commandes Pharmacies</button>
        <button onClick={() => setCurrentView('livraisons')}>Livraisons</button>
        <button onClick={handleLogout}>Se déconnecter</button>
      </nav>

      <div>
        {currentView === 'infos' && <InfosDistributeur />}
        {currentView === 'stock' && <StockDistributeur />}
        {currentView === 'centrale' && (
          <>
            <MedicamentsCentrale />
          </>
        )}
        {currentView === 'pharmacies' && <CommandesPharmacies />}
        {currentView === 'livraisons' && <Livraisons />}
      </div>
    </div>
  );
};

export default Distributeur;
