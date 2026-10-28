// src/pages/Register/Register.js
import React, { useState } from 'react';

const Register = () => {
  const [role, setRole] = useState('pharmacie');
  const [nom, setNom] = useState('');
  const [email, setEmail] = useState('');
  const [mdp, setMdp] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/demandes-comptes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nom,
          email,
          type_utilisateur: role,
          mot_de_passe: mdp
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert('Demande envoyée avec succès');
      } else {
        alert(data.detail || 'Erreur lors de l’envoi');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur réseau');
    }
  };

  return (
    <div>
      <h2>Demande de création de compte</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Nom" value={nom} onChange={e => setNom(e.target.value)} required />
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Mot de passe" value={mdp} onChange={e => setMdp(e.target.value)} required />
        <select value={role} onChange={e => setRole(e.target.value)}>
          <option value="pharmacie">Pharmacie</option>
          <option value="distributeur">Distributeur</option>
          <option value="fabricant">Fabricant</option>
        </select>
        <button type="submit">Envoyer la demande</button>
      </form>
    </div>
  );
};

export default Register;
