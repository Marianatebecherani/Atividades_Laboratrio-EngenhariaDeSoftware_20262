import { useState } from "react";

//import LoginModal from "../components/LoginModal";
//import RegisterModal from "../components/RegisterModal";

function LandingPage({
  onLogin
}) {

  const [modal, setModal] =
    useState(null);


  const closeModal = () => {
    setModal(null);
  };


  return (
    <div className="app">

      <header className="header">

        <div className="logo">

          <span className="logo-star">
            ★
          </span>

          <span>
            Film<span>Star</span>
          </span>

        </div>


        <nav className="nav">

          <button
            className="btn btn-login"
            onClick={() =>
              setModal("login")
            }
          >
            Login
          </button>


          <button
            className="btn btn-register"
            onClick={() =>
              setModal("register")
            }
          >
            Registrar
          </button>

        </nav>

      </header>


      <main>

        <section className="hero">

          <div className="hero-content">

            <div className="badge">
              ⭐ O seu lugar para falar de filmes
            </div>

            <h1>
              Descubra.
              <br />

              <span>Avalie.</span>

              <br />

              Compartilhe.
            </h1>

            <p className="hero-description">
              Encontre seus próximos filmes favoritos,
              avalie o que você assistiu e descubra
              o que outros apaixonados por cinema
              estão assistindo.
            </p>


            <div className="hero-buttons">

              <button
                className="main-button"
                onClick={() =>
                  setModal("register")
                }
              >
                Começar agora
                <span>→</span>
              </button>


              <button
                className="secondary-button"
                onClick={() =>
                  setModal("login")
                }
              >
                Já tenho uma conta
              </button>

            </div>

          </div>


          <div className="hero-visual">

            {/* conteúdo visual atual
                da sua Landing Page */}

          </div>

        </section>


        {/* FEATURES */}

        <section className="features">

          {/* suas três feature-cards atuais */}

        </section>

      </main>


      <footer className="footer">

        <div className="logo">

          <span className="logo-star">
            ★
          </span>

          <span>
            Film<span>Star</span>
          </span>

        </div>

        <p>
          Seu universo cinematográfico.
        </p>

      </footer>


      {modal === "login" && (

        <LoginModal
          onClose={closeModal}
          onLogin={onLogin}
          onRegister={() =>
            setModal("register")
          }
        />

      )}


      {modal === "register" && (

        <RegisterModal
          onClose={closeModal}
          onLogin={onLogin}
          onRegister={() =>
            setModal("login")
          }
        />

      )}

    </div>
  );
}

export default LandingPage;