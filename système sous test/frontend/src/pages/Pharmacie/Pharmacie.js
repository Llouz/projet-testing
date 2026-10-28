import React, { useState, } from 'react';
import { useNavigate } from 'react-router-dom';
import InfosPharmacie from './components/InfosPharmacie';
import StockPharmacie from './components/StockPharmacie';
import CatalogueDistributeurs from './components/CatalogueDistributeurs';
import ListeCommandes from './components/ListeCommandes';
import './Pharmacie.css';


const Pharmacie = () => {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState('infos');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  return (
    <div className="pharmacie-container">
      <h1>Espace Pharmacie</h1>
      <nav>
        <button onClick={() => setCurrentView('infos')}>Mes Infos</button>
        <button onClick={() => setCurrentView('stock')}>Mon Stock</button>
        <button onClick={() => setCurrentView('catalogue')}>Catalogue</button>
        <button onClick={() => setCurrentView('commandes')}>Commandes</button>
        <button onClick={handleLogout}>Se déconnecter</button>
      </nav>

      <div>
        {currentView === 'infos' && <InfosPharmacie />}
        {currentView === 'stock' && <StockPharmacie />}
        {currentView === 'catalogue' && <CatalogueDistributeurs />}
        {currentView === 'commandes' && <ListeCommandes />}
      </div>
    </div>
  );
};

export default Pharmacie;
