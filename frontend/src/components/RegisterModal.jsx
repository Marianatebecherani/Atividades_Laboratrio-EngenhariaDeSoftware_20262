import { useState } from "react";
import { cadastrar } from "../api";

function RegisterModal({
  onClose,
  onLogin,
  onSwitchToLogin
}) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await cadastrar(nome, email, senha);
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
          ⭐
        </div>

        <h2>
          Crie sua conta
        </h2>

        <p className="modal-description">
          Faça parte da comunidade Film Star.
        </p>


        <form onSubmit={handleSubmit}>

          <div className="input-group">

            <label>
              Nome
            </label>

            <input
              type="text"
              placeholder="Como podemos chamar você?"
              value={nome}
              onChange={(event) => setNome(event.target.value)}
              maxLength={100}
              required
            />

          </div>


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
              placeholder="Crie uma senha com ao menos 8 caracteres"
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              minLength={8}
              maxLength={128}
              required
            />

          </div>


          <button
            type="submit"
            className="modal-button"
            disabled={enviando}
          >
            {enviando ? "Criando conta..." : "Criar conta"}
          </button>

          {erro && <p className="form-error" role="alert">{erro}</p>}

        </form>


        <p className="modal-footer-text">

          Já possui uma conta?

          <button
            type="button"
            onClick={onSwitchToLogin}
          >
            Entrar
          </button>

        </p>

      </div>

    </div>
  );
}

export default RegisterModal;