export function SettingsPage() {
  return (
    <>
      <div className="page-title">
        <div>
          <h1>Configuracoes</h1>
          <p>RBAC, parametros de importacao, integracoes futuras e seguranca.</p>
        </div>
      </div>
      <section className="grid settings-grid">
        <article className="card">
          <h2>Microsoft Entra ID</h2>
          <p>Preparado para tenant, client id e escopos via variaveis seguras.</p>
        </article>
        <article className="card">
          <h2>Lansweeper API</h2>
          <p>Preparado para token, sync incremental, retry e timeout.</p>
        </article>
        <article className="card">
          <h2>Execucao integrada</h2>
          <p>Frontend estatico servido pelo FastAPI, sem CORS e sem servidor Node em producao.</p>
        </article>
        <article className="card">
          <h2>Legado preservado</h2>
          <p>Portal de assinaturas mantido em /assinaturas/ e administracao legada em /admin/.</p>
        </article>
      </section>
    </>
  );
}
