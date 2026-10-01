function LoginModal({
  onClose,
  onLogin,
  onRegister
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
              Username
            </label>

            <input
              type="text"
              placeholder="Digite seu username"
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
              required
            />

          </div>


          <button
            type="submit"
            className="modal-button"
          >
            Entrar
          </button>

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