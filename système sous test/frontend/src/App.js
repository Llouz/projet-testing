import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Admin from './pages/Admin/Admin';
import Fabricant from './pages/Fabricant/Fabricant';
import Distributeur from './pages/Distributeur/Distributeur';
import Pharmacie from './pages/Pharmacie/Pharmacie';
import Livreur from './pages/Livreur/Livreur';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/fabricant" element={<Fabricant />} />
        <Route path="/distributeur" element={<Distributeur />} />
        <Route path="/pharmacie" element={<Pharmacie />} />
        <Route path="/livreur" element={<Livreur />} />
      </Routes>
    </Router>
  );
};

export default App;
