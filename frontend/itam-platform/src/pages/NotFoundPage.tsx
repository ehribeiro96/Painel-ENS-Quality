import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="screen-center">
      <section className="card not-found">
        <h1>Pagina nao encontrada</h1>
        <p>A rota solicitada nao existe no console operacional.</p>
        <Link className="button" to="/">Voltar ao dashboard</Link>
      </section>
    </main>
  );
}
