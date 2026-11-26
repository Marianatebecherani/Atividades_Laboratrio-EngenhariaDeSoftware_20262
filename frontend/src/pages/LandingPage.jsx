import { useState } from "react";
import "../styles/LandingPage.css";

import LoginModal from "../components/LoginModal";
import RegisterModal from "../components/RegisterModal";

import LandingHeader from "../components/LandingHeader";
import LandingHero from "../components/LandingHero";
import AutoPlayMovieCarousel from "../components/AutoPlayMovieCarousel";
import LandingFooter from "../components/LandingFooter";

function LandingPage({ onLogin }) {
  const [modal, setModal] = useState(null);

  const closeModal = () => {
    setModal(null);
  };

  return (
    <div className="landing-page">
      <LandingHeader
        onLoginClick={() => setModal("login")}
        onRegisterClick={() => setModal("register")}
      />

      <div className="landing-hero-wrapper">
        <div className="landing-carousel-background" />
        <LandingHero
          onGetStarted={() => setModal("register")}
          onLoginClick={() => setModal("login")}
        />
        <AutoPlayMovieCarousel />
      </div>

      <LandingFooter />

      {modal === "login" && (
        <LoginModal
          onClose={closeModal}
          onLogin={onLogin}
          onRegister={() => setModal("register")}
        />
      )}

      {modal === "register" && (
        <RegisterModal
          onClose={closeModal}
          onLogin={onLogin}
          onSwitchToLogin={() => setModal("login")}
        />
      )}
    </div>
  );
}

export default LandingPage;