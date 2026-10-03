import { useEffect, useState } from "react";

import "./App.css";
import { entrar, obterPerfil } from "./api";

import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("filmstar-token"));
  const [usuario, setUsuario] = useState(null);
  const [sessaoCarregada, setSessaoCarregada] = useState(!token);

  useEffect(() => {
    if (!token) return;

    let ativo = true;
    obterPerfil(token)
      .then((perfil) => {
        if (ativo) setUsuario(perfil);
      })
      .catch(() => {
        localStorage.removeItem("filmstar-token");
        if (ativo) {
          setToken(null);
          setUsuario(null);
        }
      })
      .finally(() => {
        if (ativo) setSessaoCarregada(true);
      });

    return () => {
      ativo = false;
    };
  }, [token]);

  const handleLogin = async (email, senha) => {
    const resposta = await entrar(email, senha);
    localStorage.setItem("filmstar-token", resposta.access_token);
    setSessaoCarregada(false);
    setToken(resposta.access_token);
  };

  const handleLogout = () => {
    localStorage.removeItem("filmstar-token");
    setToken(null);
    setUsuario(null);
    setSessaoCarregada(true);
  };

  if (!sessaoCarregada) {
    return <main className="app-loading">Conectando à sua conta...</main>;
  }

  if (!token) {
    return (
      <LandingPage
        onLogin={handleLogin}
      />
    );
  }

  return (
    <Dashboard
      token={token}
      usuario={usuario}
      onLogout={handleLogout}
    />
  );
}

export default App;