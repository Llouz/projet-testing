import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InfosFabricant from './components/InfosFabricant';
import DemandesList from './components/DemandesList';
import NouvelleDemandeForm from './components/NouvelleDemandeForm';
import './Fabricant.css';

const Fabricant = () => {
  const [currentView, setCurrentView] = useState('infos');
  const [infos, setInfos] = useState(null);
  const [demandes, setDemandes] = useState([]);
  const [refresh, setRefresh] = useState(false);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const fetchInfos = async () => {
    try {
      const res = await fetch('http://localhost:8000/fabricant/infos', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setInfos(data);
    } catch (err) {
      console.error("Erreur lors du chargement des infos.");
    }
  };

  const fetchDemandes = async () => {
    try {
      const res = await fetch('http://localhost:8000/fabricant/demandes-medicaments', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setDemandes(data);
    } catch (err) {
      console.error("Erreur lors du chargement des demandes.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  useEffect(() => {
    fetchInfos();
    fetchDemandes();
  }, [refresh]);

  return (
    <div className="fabricant-container">
      <h1>Espace Fabricant</h1>

      <nav>
        <button onClick={() => setCurrentView('infos')}>Mes Infos</button>
        <button onClick={() => setCurrentView('demandes')}>Mes Demandes</button>
        <button onClick={() => setCurrentView('nouvelle')}>Nouvelle Demande</button>
        <button onClick={handleLogout}>Se déconnecter</button>
      </nav>

      <div>
        {currentView === 'infos' && infos && <InfosFabricant infos={infos} />}
        {currentView === 'demandes' && (
          <DemandesList demandes={demandes} onRefresh={() => setRefresh(!refresh)} />
        )}
        {currentView === 'nouvelle' && (
          <NouvelleDemandeForm onSuccess={() => setRefresh(!refresh)} />
        )}
      </div>
    </div>
  );
};

export default Fabricant;
