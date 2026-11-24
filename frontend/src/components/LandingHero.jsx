function LandingHero({ onGetStarted, onLoginClick }) {
  return (
    <section className="landing-hero">
      <div className="landing-hero-gradient"></div>

      <div className="landing-hero-container">
        <div className="landing-hero-content">
          <div className="landing-badge">
            ⭐ Seu universo cinematográfico
          </div>

          <h1 className="landing-hero-title">
            Descubra.
            <br />
            <span>Avalie.</span>
            <br />
            Compartilhe.
          </h1>

          <p className="landing-hero-description">
            Encontre seus próximos filmes favoritos, avalie o que você assistiu
            e descubra o que outros apaixonados por cinema estão assistindo.
          </p>

          <div className="landing-hero-buttons">
            <button className="landing-btn-primary" onClick={onGetStarted}>
              Começar agora
              <span>→</span>
            </button>

            <button className="landing-btn-secondary" onClick={onLoginClick}>
              Já tenho uma conta
            </button>
          </div>
        </div>

        <div className="landing-hero-visual">
          <div className="landing-glow landing-glow-pink"></div>
          <div className="landing-glow landing-glow-purple"></div>
          <div className="landing-glow landing-glow-blue"></div>
        </div>
      </div>
    </section>
  );
}

export default LandingHero;
