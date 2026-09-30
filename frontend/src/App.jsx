import { useState } from "react";

import "./App.css";

//import { movies } from "./data/movies";

import LandingPage from "./pages/LandingPage";
//import Dashboard from "./pages/Dashboard";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogin = () => {
    setLoggedIn(true);
  };

  const handleLogout = () => {
    setLoggedIn(false);
  };

  if (!loggedIn) {
    return (
      <LandingPage
        onLogin={handleLogin}
      />
    );
  }

  return (
    <Dashboard
      movies={movies}
      onLogout={handleLogout}
    />
  );
}

export default App;