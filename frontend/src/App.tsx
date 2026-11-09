
import { Navigate, NavLink, Outlet, Route, Routes } from "react-router";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import DriversPage from "./pages/DriversPage";
import PassengersPage from "./pages/PassengersPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import UsersPage from "./pages/UsersPage";
import NotFoundPage from "./pages/NotFoundPage";

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
        return <Navigate to="/cambiar-password" replace />;
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

                {usuario?.rol === "Administrador" && (
                    <NavLink to="/usuarios">
                        Usuarios
                    </NavLink>
                )}
            </nav>

            <Outlet />
        </main>
    );
}

function RutaCambioPassword() {
    const {
        autenticado,
        cargandoSesion,
        usuario
    } = useAuth();

    if (cargandoSesion) {
        return <p>Verificando sesión...</p>;
    }

    if (!autenticado) {
        return <Navigate to="/login" replace />;
    }

    if (!usuario?.cambiar_password) {
        return <Navigate to="/dashboard" replace />;
    }

    return <ChangePasswordPage />;
}

function App() {
    const { autenticado, cargandoSesion, usuario } = useAuth();

    if (cargandoSesion) {
        return <p>Verificando sesión...</p>;
    }

    return (
        <Routes>
            
            <Route path="/" element={<LandingPage />} />
            <Route path="*" element={<NotFoundPage />} />

            <Route
                path="/login"
                element={
                    autenticado
                        ? (
                            <Navigate
                                to={usuario?.cambiar_password ? "/cambiar-password" : "/dashboard"}
                                replace
                            />
                        )
                        : <LoginPage />
                }
            />

            <Route
                path="/cambiar-password"
                element={<RutaCambioPassword />}
            />

            <Route element={<RutaProtegida />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/conductores" element={<DriversPage />} />
                <Route path="/pasajeros" element={<PassengersPage />} />
                <Route path="/usuarios" element={<UsersPage />} />
            </Route>

            <Route
                path="*"
                element={<Navigate to="/" replace />}
            />
        </Routes>
    );
}

export default App;
