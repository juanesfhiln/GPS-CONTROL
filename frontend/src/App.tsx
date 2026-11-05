
import BackendStatus from "./components/BackendStatus";

function App() {
  return (
    <main className="inicio">
      <h1>GPS Control</h1>

      <p>
        Plataforma de monitoreo y gestión de flotas.
      </p>

      <BackendStatus/>

      <button>
        Iniciar sesión
      </button>
    </main>
  );
}

export default App;
