
import ChangePasswordForm from "../features/auth/components/ChangePasswordForm";
import { useAuth } from "../features/auth/context/AuthContext";

export default function ChangePasswordPage() {
    const { cerrarSesion } = useAuth();

    return (
        <main className="password-page">
            <section className="password-page__container">
                <ChangePasswordForm />

                <button
                    type="button"
                    className="password-page__logout"
                    onClick={cerrarSesion}
                >
                    Cerrar sesión
                </button>
            </section>
        </main>
    );
}
