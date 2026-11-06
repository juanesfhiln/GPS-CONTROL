
import LoginForm from "../features/auth/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="login-page">
      <section className="login-page__container">
        <h1>GPS Control</h1>

        <p>
          Ingresa tus credenciales para acceder
          a la plataforma.
        </p>

        <LoginForm />
      </section>
    </main>
  );
}
