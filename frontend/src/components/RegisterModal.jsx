function RegisterModal({
  onClose,
  onLogin
}) {

  const handleSubmit = (event) => {
    event.preventDefault();

    onLogin();
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
              Username
            </label>

            <input
              type="text"
              placeholder="Escolha seu username"
              required
            />

          </div>


          <div className="input-group">

            <label>
              Senha
            </label>

            <input
              type="password"
              placeholder="Crie uma senha"
              required
            />

          </div>


          <div className="input-group">

            <label>
              Idade
            </label>

            <input
              type="number"
              placeholder="Digite sua idade"
              min="1"
              max="120"
              required
            />

          </div>


          <button
            type="submit"
            className="modal-button"
          >
            Criar conta
          </button>

        </form>


        <p className="modal-footer-text">

          Já possui uma conta?

          <button
            type="button"
            onClick={onLogin}
          >
            Entrar
          </button>

        </p>

      </div>

    </div>
  );
}

export default RegisterModal;