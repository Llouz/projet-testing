import React, { useEffect, useState } from 'react';

const InfosPharmacie = () => {
  const [infos, setInfos] = useState(null);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const fetchInfos = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8000/pharmacie/infos', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Erreur');
        const data = await res.json();
        setInfos(data);
      } catch (e) {
        console.error(e);
        setError("Impossible de récupérer les informations.");
      }
    };
    fetchInfos();
  }, []);

  return (
    <div
      style={{
        maxWidth: 720,
        margin: '0 auto',
        padding: 24,
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        color: '#1f2d3d',
      }}
    >
      <h2
        style={{
          textAlign: 'center',
          marginBottom: 24,
          color: 'black',
          borderRadius: 10,
          fontSize: '1.75rem',
          padding: '10px 30px',
          display: 'inline-block',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      >
        Mes informations
      </h2>

      {error && (
        <div
          style={{
            background: '#fde2e2',
            color: '#a32d2d',
            padding: '10px 14px',
            borderRadius: 8,
            marginBottom: 12,
            border: '1px solid #f5c2c2',
          }}
        >
          {error}
        </div>
      )}

      {infos ? (
        <div
          style={{
            background: '#fff',
            borderRadius: 14,
            padding: 20,
            boxShadow: '0 12px 32px rgba(31,45,61,0.08)',
            display: 'grid',
            rowGap: 12,
            columnGap: 16,
            gridTemplateColumns: '150px 1fr',
            alignItems: 'start',
          }}
        >
          <div style={{ fontWeight: 600 }}>ID :</div>
          <div>{infos.id}</div>

          <div style={{ fontWeight: 600 }}>Nom :</div>
          <div>{infos.nom}</div>

          <div style={{ fontWeight: 600 }}>Email :</div>
          <div>{infos.email}</div>

          <div style={{ fontWeight: 600 }}>Mot de passe :</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type={showPassword ? 'text' : 'password'}
              value={infos.mot_de_passe}
              readOnly
              style={{
                fontFamily: 'monospace',
                background: '#f5f5f5',
                padding: '4px 8px',
                borderRadius: 4,
                border: '1px solid #ccc',
              }}
            />
            <button
              onClick={() => setShowPassword((prev) => !prev)}
              style={{
                padding: '6px 12px',
                borderRadius: 4,
                border: '1px solid #1f78c1',
                background: showPassword ? '#fff' : '#1f78c1',
                color: showPassword ? '#1f78c1' : '#fff',
                cursor: 'pointer',
                fontSize: 12,
              }}
            >
              {showPassword ? 'Cacher' : 'Afficher'}
            </button>
          </div>

          <div style={{ fontWeight: 600 }}>Distributeur :</div>
          <div>{infos.distributeur_id ?? 'Aucun'}</div>

          <div style={{ fontWeight: 600 }}>Type :</div>
          <div>{infos.type_utilisateur}</div>

          
        </div>
      ) : (
        !error && <p style={{ textAlign: 'center' }}>Chargement...</p>
      )}
    </div>
  );
};

export default InfosPharmacie;
