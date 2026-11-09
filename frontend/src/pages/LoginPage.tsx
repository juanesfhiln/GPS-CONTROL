
import LoginForm from "../features/auth/components/LoginForm";

export default function LoginPage() {
    return (
        <main className="login-page">
            <section className="login-page__container">
                <h1>GPS CONTROL</h1>

                <p>
                    Plataforma de monitoreo y gestión de flotas.
                    Ingresa tus credenciales para continuar.
                </p>

                <LoginForm />
            </section>
        </main>
    );
}
