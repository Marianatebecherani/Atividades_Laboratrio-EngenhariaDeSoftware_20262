import { useState } from "react";

function LoginModal({
  onClose,
  onLogin,
  onRegister
}) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await onLogin(email, senha);
      onClose();
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  };


  return (
    <div
      className="modal-overlay"
      onClick={onClose}
    >

      <div
        className="modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        <button
          className="modal-close"
          onClick={onClose}
        >
          ×
        </button>


        <div className="modal-icon">
          🔐
        </div>

        <h2>
          Bem-vindo de volta!
        </h2>

        <p className="modal-description">
          Entre na sua conta para continuar
          sua jornada pelo mundo do cinema.
        </p>


        <form onSubmit={handleSubmit}>

          <div className="input-group">

            <label>
              E-mail
            </label>

            <input
              type="email"
              placeholder="voce@exemplo.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

          </div>


          <div className="input-group">

            <label>
              Senha
            </label>

            <input
              type="password"
              placeholder="Digite sua senha"
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              required
            />

          </div>


          <button
            type="submit"
            className="modal-button"
            disabled={enviando}
          >
            {enviando ? "Entrando..." : "Entrar"}
          </button>

          {erro && <p className="form-error" role="alert">{erro}</p>}

        </form>


        <p className="modal-footer-text">

          Ainda não possui uma conta?

          <button
            type="button"
            onClick={onRegister}
          >
            Registrar
          </button>

        </p>

      </div>

    </div>
  );
}

export default LoginModal;