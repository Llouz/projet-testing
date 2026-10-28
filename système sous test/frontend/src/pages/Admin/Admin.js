import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Utilisateurs from './components/Utilisateurs';
import DemandesComptes from './components/DemandesComptes';
import DemandesMedicaments from './components/DemandesMedicaments';
import StockCentrale from './components/StockCentrale';
import DemandesStockDistributeur from './components/DemandesStockDistributeur';
import './Admin.css';

const Admin = () => {
  const [currentView, setCurrentView] = useState('utilisateurs');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  return (
    <div className="admin-container">
      <h1>Espace Pharmacie Centrale</h1>

      <nav>
        <button onClick={() => setCurrentView('utilisateurs')}>Utilisateurs</button>
        <button onClick={() => setCurrentView('demandes')}>Demandes de comptes</button>
        <button onClick={() => setCurrentView('medicaments')}>Demandes de médicaments</button>
        <button onClick={() => setCurrentView('stock')}>Stock central</button>
        <button onClick={() => setCurrentView('demandes_stock')}>Demandes distributeurs</button>
        <button onClick={handleLogout}>Se déconnecter</button>
      </nav>

      <div>
        {currentView === 'utilisateurs' && <Utilisateurs />}
        {currentView === 'demandes' && <DemandesComptes />}
        {currentView === 'medicaments' && <DemandesMedicaments />}
        {currentView === 'stock' && <StockCentrale />}
        {currentView === 'demandes_stock' && <DemandesStockDistributeur />}
      </div>
    </div>
  );
};

export default Admin;
