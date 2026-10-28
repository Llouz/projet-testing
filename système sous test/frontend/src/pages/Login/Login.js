import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [role, setRole] = useState('pharmacie');
  const [nom, setNom] = useState('');
  const [emailDemande, setEmailDemande] = useState('');
  const [mdpDemande, setMdpDemande] = useState('');
  const [distributeurId, setDistributeurId] = useState('');

  const [distributeurs, setDistributeurs] = useState([]);
  const [loadingDistributeurs, setLoadingDistributeurs] = useState(false);
  const [errorDistributeurs, setErrorDistributeurs] = useState(null);
  const [filterText, setFilterText] = useState('');

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password: password }),
      });
      const data = await res.json();
      if (res.ok) {
        const payload = JSON.parse(atob(data.access_token.split('.')[1]));
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', payload.type_utilisateur);

        switch (payload.type_utilisateur) {
          case 'admin': navigate('/admin'); break;
          case 'fabricant': navigate('/fabricant'); break;
          case 'distributeur': navigate('/distributeur'); break;
          case 'pharmacie': navigate('/pharmacie'); break;
          case 'livreur': navigate('/livreur'); break;
          default: alert('Rôle inconnu');
        }
      } else {
        alert(data.detail || 'Erreur de connexion');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur lors de la connexion');
    }
  };

  const handleDemandeCompteCombinée = async (e) => {
    e.preventDefault();
    try {
      let url = '';
      let body = {};

      if (role === 'livreur') {
        if (!distributeurId) {
          alert('Veuillez sélectionner un distributeur pour le livreur.');
          return;
        }
        url = 'http://localhost:8000/demandes-livreur';
        body = {
          nom,
          email: emailDemande,
          mot_de_passe: mdpDemande,
          distributeur_id: parseInt(distributeurId, 10),
        };
      } else {
        url = 'http://localhost:8000/demandes-comptes';
        body = {
          nom,
          email: emailDemande,
          type_utilisateur: role,
          mot_de_passe: mdpDemande,
        };
      }

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (res.ok) {
        alert('Demande envoyée avec succès');
        setNom('');
        setEmailDemande('');
        setMdpDemande('');
        setDistributeurId('');
        setRole('pharmacie');
      } else {
        alert(data.detail || 'Erreur lors de l’envoi');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur réseau');
    }
  };

  useEffect(() => {
    const fetchDistributeurs = async () => {
      setLoadingDistributeurs(true);
      setErrorDistributeurs(null);
      try {
        const res = await fetch('http://localhost:8000/distributeurs');
        const data = await res.json();
        if (res.ok) {
          setDistributeurs(data);
        } else {
          setErrorDistributeurs(data.detail || 'Erreur chargement');
        }
      } catch (err) {
        console.error(err);
        setErrorDistributeurs('Erreur réseau');
      } finally {
        setLoadingDistributeurs(false);
      }
    };
    fetchDistributeurs();
  }, []);

  const filtered = distributeurs.filter(
    (d) =>
      d.nom.toLowerCase().includes(filterText.toLowerCase()) ||
      String(d.id).includes(filterText)
  );

  return (
    <div className="login-container">
      <h2>{showRegister ? 'Créer un compte' : 'Connexion'}</h2>

      {!showRegister && (
        <form onSubmit={handleLogin} className="mb-4">
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <button type="submit">Se connecter</button>
        </form>
      )}

      <button className="toggle-button" onClick={() => setShowRegister((prev) => !prev)}>
        {showRegister ? 'Se connecter' : 'Créer un compte'}
      </button>

      {showRegister && (
        <div className="flex gap-8 mt-6">
          <div className="w-1/2">
            <h3>Demande de création de compte</h3>
            <form onSubmit={handleDemandeCompteCombinée} className="space-y-4">
              <label>Nom<input type="text" value={nom} onChange={(e) => setNom(e.target.value)} required /></label>
              <label>Email<input type="email" value={emailDemande} onChange={(e) => setEmailDemande(e.target.value)} required /></label>
              <label>Mot de passe<input type="password" value={mdpDemande} onChange={(e) => setMdpDemande(e.target.value)} required /></label>
              <label>Rôle<select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="pharmacie">Pharmacie</option>
                <option value="distributeur">Distributeur</option>
                <option value="fabricant">Fabricant</option>
                <option value="livreur">Livreur</option>
              </select></label>

              {role === 'livreur' && (
                <>
                  <label>ID Distributeur<input type="text" value={distributeurId} readOnly required /></label>
                  <div>
                    <p>Attribuer au distributeur :</p>
                    <input type="text" placeholder="Filtrer par nom ou ID" value={filterText} onChange={(e) => setFilterText(e.target.value)} className="w-full p-2 border rounded" />
                    <div className="max-h-[250px] overflow-auto border rounded p-2">
                      {loadingDistributeurs && <div>Chargement des distributeurs...</div>}
                      {errorDistributeurs && <div className="text-red-600">{errorDistributeurs}</div>}
                      {!loadingDistributeurs && !errorDistributeurs && (
                        filtered.length === 0 ? <div>Aucun distributeur trouvé.</div> :
                          filtered.map((d) => (
                            <div key={d.id} className={`distributeur-item ${String(d.id) === String(distributeurId) ? 'selected' : ''}`} onClick={() => setDistributeurId(d.id)}>
                              <span><strong>{d.nom}</strong> (ID: {d.id})</span>
                            </div>
                          ))
                      )}
                    </div>
                    <small>Cliquer sur un distributeur pour pré-remplir son ID.</small>
                  </div>
                </>
              )}
              <button type="submit">{role === 'livreur' ? 'Envoyer demande livreur' : 'Envoyer demande'}</button>
            </form>
          </div>
          <div className="w-1/2">
            <h3>Informations</h3>
            <p>Choisis un rôle dans le menu déroulant. Si tu sélectionnes <strong>Livreur</strong>, tu dois aussi assigner un distributeur en le sélectionnant dans la liste filtrable et le champ ID Distributeur se remplira automatiquement.</p>
            {role !== 'livreur' && <p>Pour les rôles Pharmacie / Distributeur / Fabricant, aucun distributeur n'est nécessaire.</p>}
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
