
import { Navigate, NavLink, Outlet, Route, Routes } from "react-router";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import DriversPage from "./pages/DriversPage";
import PassengersPage from "./pages/PassengersPage";

import ChangePasswordForm from "./features/auth/components/ChangePasswordForm";
import { useAuth } from "./features/auth/context/AuthContext";

function RutaProtegida() {
    const {
        autenticado,
        cargandoSesion,
        usuario,
        cerrarSesion
    } = useAuth();

    if (cargandoSesion) {
        return <p>Verificando sesión...</p>;
    }

    if (!autenticado) {
        return <Navigate to="/login" replace />;
    }

    if (usuario?.cambiar_password) {
        return (
            <main>
                <ChangePasswordForm />

                <button onClick={cerrarSesion}>
                    Cerrar sesión
                </button>
            </main>
        );
    }

    return (
        <main className="dashboard-layout">
            <header className="dashboard-layout__header">
                <div>
                    <span className="dashboard-layout__label">
                        GPS CONTROL
                    </span>

                    <p className="dashboard-layout__welcome">
                        Bienvenido, <strong>{usuario?.nombre}</strong>
                    </p>
                </div>

                <button
                    className="dashboard-layout__logout"
                    onClick={cerrarSesion}
                >
                    Cerrar sesión
                </button>
            </header>

            <nav className="dashboard-layout__nav" aria-label="Navegación principal">
                <NavLink to="/dashboard">
                    Dashboard
                </NavLink>

                <NavLink to="/conductores">
                    Conductores
                </NavLink>

                <NavLink to="/pasajeros">
                    Pasajeros
                </NavLink>
            </nav>

            <Outlet />
        </main>
    );
}

function App() {
    const { autenticado, cargandoSesion } = useAuth();

    if (cargandoSesion) {
        return <p>Verificando sesión...</p>;
    }

    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />

            <Route
                path="/login"
                element={
                    autenticado
                        ? <Navigate to="/dashboard" replace />
                        : <LoginPage />
                }
            />

            <Route element={<RutaProtegida />}>
                <Route path="/dashboard" element={<DashboardPage />}/>
                <Route path="/conductores" element={<DriversPage />} />
                <Route path="/pasajeros" element={<PassengersPage />} />
            </Route>

            <Route
                path="*"
                element={<Navigate to="/" replace />}
            />
        </Routes>
    );
}

export default App;
