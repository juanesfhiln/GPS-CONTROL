import { Link } from "react-router";

function NotFoundPage() {
    return (
        <main className="not-found">
            <div className="not-found__content">
                <span className="not-found__code">404</span>

                <h1>Página no encontrada</h1>

                <p>
                    La dirección que intentas visitar no existe
                    o no está disponible.
                </p>

                <Link to="/" className="not-found__button">
                    Volver al inicio
                </Link>
            </div>
        </main>
    );
}

export default NotFoundPage;