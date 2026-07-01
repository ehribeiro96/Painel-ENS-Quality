import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, RefreshCcw, Search, ShieldAlert } from "lucide-react";
import { RagCollectionFilter } from "../components/RagCollectionFilter";
import { RagSearchResults } from "../components/RagSearchResults";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { getRagAuditRecent, getRagCollections, getRagCourseContext, searchRag } from "../lib/apoemaRagApi";
import { useAuth } from "@/lib/auth";
import type { RagCollectionId } from "../types";
import type { RagAuditEntry, RagCollection, RagCourseContext, RagSearchResult } from "../lib/apoemaRagApi";

type CollectionState = "loading" | "ready" | "empty" | "unauthorized" | "forbidden" | "unavailable" | "error";
type SearchState = "idle" | "loading" | "ready" | "empty" | "unauthorized" | "forbidden" | "not_found" | "expired" | "rate_limited" | "unavailable" | "error";
type BannerTone = "warning" | "danger" | "success";

type Banner = {
  title: string;
  message: string;
  tone: BannerTone;
};

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function describeError(error: unknown, resource: string): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sessão necessária", message: `Faça login novamente para acessar ${resource}.` };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: `Seu perfil não tem permissão para consultar ${resource}.` };
    if (error.kind === "not_found") return { tone: "warning", title: "Recurso não encontrado", message: `O backend não retornou ${resource}.` };
    if (error.kind === "expired") return { tone: "warning", title: "Recurso expirado", message: `O backend informou que ${resource} não está mais disponível.` };
    if (error.kind === "rate_limited") return { tone: "warning", title: "Limite atingido", message: `Espere alguns instantes para consultar ${resource} novamente.` };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Backend indisponível", message: `Falha de rede ao consultar ${resource}.` };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: `Falha ao consultar ${resource}.` };
}

function collectionStateFromError(error: unknown): CollectionState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

function searchStateFromError(error: unknown): SearchState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "not_found") return "not_found";
    if (error.kind === "expired") return "expired";
    if (error.kind === "rate_limited") return "rate_limited";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

export function RagPage() {
  const { token } = useAuth();
  const [collections, setCollections] = useState<RagCollection[]>([]);
  const [collectionsState, setCollectionsState] = useState<CollectionState>("loading");
  const [selectedCollections, setSelectedCollections] = useState<RagCollectionId[]>([]);
  const [query, setQuery] = useState("política institucional");
  const [results, setResults] = useState<RagSearchResult[]>([]);
  const [searchState, setSearchState] = useState<SearchState>("idle");
  const [courseContext, setCourseContext] = useState<RagCourseContext | null>(null);
  const [courseState, setCourseState] = useState<CollectionState>("loading");
  const [courseBanner, setCourseBanner] = useState<Banner | null>(null);
  const [auditEntries, setAuditEntries] = useState<RagAuditEntry[]>([]);
  const [auditState, setAuditState] = useState<CollectionState>("loading");
  const [auditBanner, setAuditBanner] = useState<Banner | null>(null);
  const [banner, setBanner] = useState<Banner | null>(null);

  const selectedCollectionLabel = useMemo(() => {
    if (selectedCollections.length === 0) {
      return "Todas as collections";
    }
    if (selectedCollections.length === 1) {
      return collections.find((collection) => collection.id === selectedCollections[0])?.label ?? "Collection selecionada";
    }
    return `${selectedCollections.length} collections selecionadas`;
  }, [collections, selectedCollections]);

  async function reload(guard: () => boolean = () => true) {
    setCollectionsState("loading");
    setCourseState("loading");
    setAuditState("loading");
    setCourseBanner(null);
    setAuditBanner(null);
    setBanner(null);

    const collectionPromise = getRagCollections(token);
    const coursePromise = getRagCourseContext("apoema-onboarding", token);
    const auditPromise = getRagAuditRecent(8, token);

    try {
      const collectionResult = await collectionPromise;
      if (!guard()) return;
      setCollections(collectionResult);
      setCollectionsState(collectionResult.length > 0 ? "ready" : "empty");
      setSelectedCollections((current) => current.filter((collectionId) => collectionResult.some((item) => item.id === collectionId)));
    } catch (error) {
      if (!guard()) return;
      setCollections([]);
      setCollectionsState(collectionStateFromError(error));
      setBanner(describeError(error, "catalogo RAG"));
    }

    try {
      const contextResult = await coursePromise;
      if (!guard()) return;
      setCourseContext(contextResult);
      setCourseState("ready");
    } catch (error) {
      if (!guard()) return;
      setCourseContext(null);
      setCourseState(collectionStateFromError(error));
      setCourseBanner(describeError(error, "contexto de curso"));
    }

    try {
      const auditResult = await auditPromise;
      if (!guard()) return;
      setAuditEntries(auditResult.items);
      setAuditState(auditResult.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      if (!guard()) return;
      setAuditEntries([]);
      setAuditState(collectionStateFromError(error));
      setAuditBanner(describeError(error, "auditoria recente"));
    }
  }

  useEffect(() => {
    let active = true;
    void reload(() => active);
    return () => {
      active = false;
    };
  }, [token]);

  async function handleSearch() {
    const normalized = query.trim();
    if (!normalized) {
      setBanner({ tone: "warning", title: "Consulta vazia", message: "Digite um termo para consultar o backend RAG." });
      return;
    }

    setSearchState("loading");
    setBanner(null);
    try {
      const result = await searchRag({ query: normalized, collections: selectedCollections, limit: 8 }, token);
      setResults(result.items);
      setSearchState(result.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      setResults([]);
      setSearchState(searchStateFromError(error));
      setBanner(describeError(error, "busca RAG"));
    }
  }

  async function handleCopyReference(reference: string) {
    try {
      await navigator.clipboard.writeText(reference);
      setBanner({ tone: "success", title: "Referência copiada", message: "A referência segura do documento foi copiada para a área de transferência." });
    } catch {
      setBanner({ tone: "warning", title: "Não foi possível copiar", message: "Seu navegador bloqueou o acesso à área de transferência." });
    }
  }

  return (
    <div className="apoema-page apoema-rag-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="warning">Mock determinístico</StatusPill>
          <h1>RAG Institucional</h1>
          <p>Busca read-only em collections institucionais via backend. RAG MCP Mock mantido para validação do contrato.</p>
        </div>
        <div className="apoema-rag-page-actions">
          <Link className="apoema-secondary-button" to="courses/apoema-onboarding">
            <BookOpen size={16} />
            Ver contexto de curso
          </Link>
          <button type="button" className="apoema-secondary-button" onClick={() => void reload()}>
            <RefreshCcw size={16} />
            Recarregar
          </button>
        </div>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Mock determinístico controlado</strong>
          <p>MCP real, vector store e provider real não estão ativos nesta fase. A UI não chama runtime externo direto.</p>
        </div>
      </div>

      {banner ? (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      ) : null}

      <section className="apoema-rag-layout">
        <div className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="info">Collections backend</StatusPill>
              <h2>Escopo e consulta</h2>
            </div>
            <span>{selectedCollectionLabel}</span>
          </div>

          {collectionsState === "loading" ? <div className="apoema-empty-state">Carregando catálogo RAG...</div> : null}
          {collectionsState === "empty" ? (
            <div className="apoema-empty-state">
              <strong>Nenhuma collection</strong>
              <p>O backend respondeu catálogo vazio.</p>
            </div>
          ) : null}
          {collectionsState === "unauthorized" ? (
            <div className="apoema-empty-state">
              <strong>Sessão necessária</strong>
              <p>Faça login novamente para consultar o catálogo RAG.</p>
            </div>
          ) : null}
          {collectionsState === "forbidden" ? (
            <div className="apoema-empty-state">
              <strong>Sem permissão</strong>
              <p>Seu perfil não tem acesso ao catálogo RAG.</p>
            </div>
          ) : null}
          {collectionsState === "unavailable" ? (
            <div className="apoema-empty-state">
              <strong>Backend indisponível</strong>
              <p>A interface não oferece fallback falso para o catálogo.</p>
            </div>
          ) : null}
          {collectionsState === "error" ? (
            <div className="apoema-empty-state">
              <strong>Erro operacional</strong>
              <p>Falha ao carregar o catálogo RAG.</p>
            </div>
          ) : null}

          {collections.length > 0 ? (
            <RagCollectionFilter
              collections={collections}
              selectedCollections={selectedCollections}
              onChange={setSelectedCollections}
              loading={collectionsState === "loading"}
              error={collectionsState === "error" ? "Não foi possível recuperar o catálogo de collections." : null}
            />
          ) : null}

          <form
            className="apoema-rag-search-form"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSearch();
            }}
          >
            <label className="apoema-field">
              Buscar no RAG
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ex.: política institucional, onboarding, segurança"
              />
            </label>
            <button type="submit" className="apoema-primary-button" disabled={searchState === "loading"}>
              <Search size={16} />
              {searchState === "loading" ? "Buscando..." : "Buscar"}
            </button>
          </form>
        </div>

        <aside className="apoema-rag-sidepanels">
          <section className="apoema-panel">
            <div className="apoema-section-head">
              <div>
                <StatusPill tone="info">Contexto de curso</StatusPill>
                <h2>apoema-onboarding</h2>
              </div>
              <span>{courseState === "ready" ? "backend-backed" : courseState}</span>
            </div>
          {courseState === "ready" && courseContext ? (
            <div className="apoema-rag-sidecard">
              <strong>{courseContext.title}</strong>
              <p>{courseContext.summary}</p>
              <small>Público: {courseContext.audience}</small>
                <ul className="apoema-rag-bullet-list">
                  {courseContext.recommendations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                <Link className="apoema-secondary-button" to={`courses/${courseContext.course_id}`}>
                  <BookOpen size={16} />
                  Abrir contexto
                </Link>
              </div>
            ) : (
              <>
                {courseBanner ? (
                  <div className={`apoema-warning ${courseBanner.tone === "danger" ? "is-danger" : "is-warning"}`}>
                    <ShieldAlert size={16} />
                    <div>
                      <strong>{courseBanner.title}</strong>
                      <p>{courseBanner.message}</p>
                    </div>
                  </div>
                ) : null}
                <div className="apoema-empty-state">
                  <strong>Contexto indisponível</strong>
                  <p>O backend ainda não respondeu o contexto de curso.</p>
                </div>
              </>
            )}
          </section>

          <section className="apoema-panel">
            <div className="apoema-section-head">
              <div>
                <StatusPill tone="warning">Auditoria recente</StatusPill>
                <h2>Eventos RAG</h2>
              </div>
              <span>{auditState === "ready" ? `${auditEntries.length} evento(s)` : auditState}</span>
            </div>
            {auditState === "ready" ? (
              <div className="apoema-rag-audit-list">
                {auditEntries.map((entry) => (
                  <article key={entry.event_id} className="apoema-rag-audit-item">
                    <strong>{entry.event_type}</strong>
                    <span>{entry.result}</span>
                    <small>
                      {entry.actor_role} · {entry.collection ?? "sem collection"} · {formatDate(entry.occurred_at)}
                    </small>
                  </article>
                ))}
              </div>
            ) : (
              <>
                {auditBanner ? (
                  <div className={`apoema-warning ${auditBanner.tone === "danger" ? "is-danger" : "is-warning"}`}>
                    <ShieldAlert size={16} />
                    <div>
                      <strong>{auditBanner.title}</strong>
                      <p>{auditBanner.message}</p>
                    </div>
                  </div>
                ) : null}
                <div className="apoema-empty-state">
                  <strong>Auditoria indisponível</strong>
                  <p>O endpoint pode exigir perfil ADMIN/MANAGER.</p>
                </div>
              </>
            )}
          </section>
        </aside>
      </section>

      <RagSearchResults
        results={results}
        loading={searchState === "loading"}
        error={
          searchState === "unauthorized"
            ? "Sua sessão expirou ou não foi autenticada."
            : searchState === "forbidden"
              ? "Você não tem permissão para consultar o RAG."
              : searchState === "not_found"
                ? "Resultado ou documento não encontrado."
                : searchState === "expired"
                  ? "Este recurso não está mais disponível."
                  : searchState === "rate_limited"
                    ? "Limite de consultas atingido. Tente novamente mais tarde."
                    : searchState === "unavailable"
                      ? "Falha de rede ao consultar o RAG."
                      : searchState === "error"
                        ? "Backend RAG indisponível."
                        : null
        }
        query={query.trim()}
        toDocumentPath={(documentId) => `documents/${documentId}`}
        onCopyReference={handleCopyReference}
      />
    </div>
  );
}
