function LandingFooter() {
  return (
    <footer className="landing-footer">
      <div className="landing-footer-container">
        <div className="landing-footer-content">
          <div className="landing-footer-section">
            <div className="landing-footer-logo">
              <span className="landing-footer-logo-star">★</span>
              <span>Film<span>Star</span></span>
            </div>
            <p className="landing-footer-tagline">
              Seu universo cinematográfico
            </p>
          </div>

          <div className="landing-footer-section">
            <h4>Plataforma</h4>
            <ul>
              <li><a href="/">Início</a></li>
              <li><a href="/#sobre">Sobre</a></li>
              <li><a href="/#termos">Termos de Uso</a></li>
              <li><a href="/#privacidade">Privacidade</a></li>
            </ul>
          </div>

          <div className="landing-footer-section">
            <h4>Comunidade</h4>
            <ul>
              <li><a href="/">Descobrir</a></li>
              <li><a href="/">Explorar</a></li>
              <li><a href="/">Listas</a></li>
              <li><a href="/">Colaborar</a></li>
            </ul>
          </div>

          <div className="landing-footer-section">
            <h4>Suporte</h4>
            <ul>
              <li><a href="/">Central de Ajuda</a></li>
              <li><a href="/">Contato</a></li>
              <li><a href="/">FAQ</a></li>
              <li><a href="/">Feedback</a></li>
            </ul>
          </div>
        </div>

        <div className="landing-footer-bottom">
          <p>&copy; 2024 FilmStar. Todos os direitos reservados.</p>
          <div className="landing-footer-links">
            <a href="/">Privacidade</a>
            <a href="/">Termos</a>
            <a href="/">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default LandingFooter;
