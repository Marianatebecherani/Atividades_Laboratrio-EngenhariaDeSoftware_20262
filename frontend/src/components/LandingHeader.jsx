function LandingHeader({ onLoginClick, onRegisterClick }) {
  return (
    <header className="landing-header">
      <div className="landing-header-container">
        <div className="landing-logo">
          <span className="landing-logo-star">★</span>
          <span>Film<span>Star</span></span>
        </div>

        <nav className="landing-nav">
          <button
            className="landing-btn landing-btn-login"
            onClick={onLoginClick}
          >
            Login
          </button>

          <button
            className="landing-btn landing-btn-register"
            onClick={onRegisterClick}
          >
            Registrar
          </button>
        </nav>
      </div>
    </header>
  );
}

export default LandingHeader;
