import React, { useEffect, useState } from 'react';
import api from '../../../utils/api';

const Utilisateurs = () => {
  const [utilisateurs, setUtilisateurs] = useState([]);
  const [error, setError] = useState('');
  // ensemble des ids dont le mot de passe est visible
  const [visiblePasswords, setVisiblePasswords] = useState(new Set());

  useEffect(() => {
    api.get('/admin/utilisateurs')
      .then(res => setUtilisateurs(res.data))
      .catch(() => setError("Erreur lors du chargement des utilisateurs."));
  }, []);

  const togglePassword = (id) => {
    setVisiblePasswords(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
        // auto-recache après 5 secondes
        setTimeout(() => {
          setVisiblePasswords(current => {
            const updated = new Set(current);
            updated.delete(id);
            return updated;
          });
        }, 5000);
      }
      return next;
    });
  };

  const mask = (pwd) => {
    if (!pwd) return '';
    return '•'.repeat(8); // masque fixe, ne révèle pas la longueur
  };

  return (
    <div style={{ padding: 16 }}>
      <h3>Utilisateurs enregistrés</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {utilisateurs.length === 0 ? (
        <p>Aucun utilisateur trouvé.</p>
      ) : (
        <table
          border="1"
          cellPadding="8"
          style={{ borderCollapse: 'collapse', width: '100%', fontFamily: 'sans-serif' }}
        >
          <thead style={{ background: '#f0f0f0' }}>
            <tr>
              <th>ID</th>
              <th>Nom</th>
              <th>Email</th>
              <th>Mot de passe</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {utilisateurs.map(u => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.nom}</td>
                <td>{u.email}</td>
                <td style={{ position: 'relative' }}>
                  <span style={{ fontFamily: 'monospace', marginRight: 8 }}>
                    {visiblePasswords.has(u.id) ? u.mot_de_passe : mask(u.mot_de_passe)}
                  </span>
                  <button
                    onClick={() => togglePassword(u.id)}
                    aria-label={visiblePasswords.has(u.id) ? 'Cacher le mot de passe' : 'Afficher le mot de passe'}
                    style={{
                      cursor: 'pointer',
                      padding: '4px 8px',
                      fontSize: 12,
                      borderRadius: 4,
                      border: '1px solid #888',
                      background: '#fff'
                    }}
                  >
                    {visiblePasswords.has(u.id) ? 'Cacher' : 'Afficher'}
                  </button>
                </td>
                <td>{u.type_utilisateur}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Utilisateurs;
