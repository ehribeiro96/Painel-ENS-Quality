import { useEffect, useMemo, useState } from "react";
import { BookOpen, RotateCcw, Search, ShieldAlert } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { getRagCourseContext, getRagRecentAudit, listRagCollections, searchRag } from "../lib/apoemaRagApi";
import { ApoemaApiError } from "../types";
import { useAuth } from "@/lib/auth";
import type { ApoemaRagAuditEntry, ApoemaRagCollection, ApoemaRagCourseContext, ApoemaRagSearchResult } from "../lib/apoemaRagApi";

type PageState = "loading" | "ready" | "empty" | "unauthorized" | "unavailable" | "error";

type Banner = {
  title: string;
  message: string;
  tone: "warning" | "danger" | "success";
};

function describeError(error: unknown, resource: string): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sessão necessária", message: `Faça login novamente para acessar ${resource}.` };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: `Seu perfil não tem permissão para consultar ${resource}.` };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Backend indisponível", message: `Não foi possível alcançar ${resource} em /api/v1.` };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: `Falha ao consultar ${resource}.` };
}

function stateFromError(error: unknown): PageState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required" || error.kind === "forbidden") return "unauthorized";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "data indisponível";
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function RagPage() {
  const { token } = useAuth();
  const [collections, setCollections] = useState<ApoemaRagCollection[]>([]);
  const [selectedCollection, setSelectedCollection] = useState("");
  const [query, setQuery] = useState("política de matrícula");
  const [results, setResults] = useState<ApoemaRagSearchResult[]>([]);
  const [courseContext, setCourseContext] = useState<ApoemaRagCourseContext | null>(null);
  const [auditEntries, setAuditEntries] = useState<ApoemaRagAuditEntry[]>([]);
  const [state, setState] = useState<PageState>("loading");
  const [searchState, setSearchState] = useState<PageState>("empty");
  const [banner, setBanner] = useState<Banner | null>(null);

  const selectedCollectionLabel = useMemo(() => {
    return collections.find((collection) => collection.id === selectedCollection)?.label ?? "Todas as collections";
  }, [collections, selectedCollection]);

  async function reload(guard: () => boolean = () => true) {
    setState("loading");
    setBanner(null);
    try {
      const [collectionResult, contextResult] = await Promise.all([
        listRagCollections(token),
        getRagCourseContext("apoema-onboarding", token).catch((error: unknown) => {
          setBanner(describeError(error, "contexto de curso"));
          return null;
        }),
      ]);
      let auditResult: ApoemaRagAuditEntry[] = [];
      try {
        auditResult = (await getRagRecentAudit(token)).items;
      } catch (error) {
        setBanner(describeError(error, "auditoria RAG"));
      }
      if (!guard()) return;
      setCollections(collectionResult);
      setSelectedCollection((current) => current || collectionResult[0]?.id || "");
      setCourseContext(contextResult);
      setAuditEntries(auditResult);
      setState(collectionResult.length > 0 ? "ready" : "empty");
    } catch (error) {
      if (!guard()) return;
      setCollections([]);
      setState(stateFromError(error));
      setBanner(describeError(error, "RAG mock"));
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
    if (!normalized) return;
    setSearchState("loading");
    setBanner(null);
    try {
      const collectionIds = selectedCollection ? [selectedCollection] : [];
      const result = await searchRag(normalized, collectionIds, token);
      setResults(result.items);
      setSearchState(result.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      setResults([]);
      setSearchState(stateFromError(error));
      setBanner(describeError(error, "pesquisa RAG"));
    }
  }

  return (
    <div className="apoema-page apoema-stub-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="warning">Mock determinístico</StatusPill>
          <h1>RAG MCP Mock</h1>
          <p>Consulta determinística backend-owned para collections, busca, contexto de curso e auditoria recente via /api/v1.</p>
        </div>
        <button type="button" className="apoema-secondary-button" onClick={() => void reload()}>
          <RotateCcw size={16} />
          Recarregar
        </button>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Mock determinístico controlado</strong>
          <p>MCP real, vector store e provider real não estão ativos nesta fase. A UI não chama runtime externo direto.</p>
        </div>
      </div>

      {banner && (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      )}

      <section className="apoema-stub-grid">
        <article className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="info">Collections</StatusPill>
              <h2>Catálogo backend</h2>
            </div>
            <span>{state}</span>
          </div>
          {state === "loading" && <div className="apoema-empty-state">Carregando collections...</div>}
          {state === "empty" && <div className="apoema-empty-state"><strong>Nenhuma collection</strong><p>O backend retornou catálogo vazio.</p></div>}
          {state === "unauthorized" && <div className="apoema-empty-state"><strong>Sessão/permissão necessária</strong><p>Chamada recusada pelo backend.</p></div>}
          {state === "unavailable" && <div className="apoema-empty-state"><strong>Backend indisponível</strong><p>Sem fallback falso local.</p></div>}
          {state === "error" && <div className="apoema-empty-state"><strong>Erro operacional</strong><p>Falha ao carregar collections.</p></div>}
          {collections.length > 0 && (
            <div className="apoema-card-list">
              {collections.map((collection) => (
                <button key={collection.id} type="button" className={`apoema-stub-card ${selectedCollection === collection.id ? "is-active" : ""}`} onClick={() => setSelectedCollection(collection.id)}>
                  <strong>{collection.label}</strong>
                  <span>{collection.description}</span>
                  <small>{collection.document_count} docs · {formatDate(collection.updated_at)}</small>
                </button>
              ))}
            </div>
          )}
        </article>

        <article className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="warning">Busca mock</StatusPill>
              <h2>Pesquisar contexto</h2>
            </div>
            <span>{selectedCollectionLabel}</span>
          </div>
          <div className="apoema-form-stack">
            <label className="apoema-field">Collection
              <select value={selectedCollection} onChange={(event) => setSelectedCollection(event.target.value)}>
                <option value="">Todas</option>
                {collections.map((collection) => <option key={collection.id} value={collection.id}>{collection.label}</option>)}
              </select>
            </label>
            <label className="apoema-field">Termo de busca
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar nos documentos mock" />
            </label>
            <button type="button" className="apoema-primary-button" onClick={() => void handleSearch()}>
              <Search size={16} />
              Pesquisar
            </button>
          </div>
        </article>
      </section>

      <section className="apoema-panel">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Resultados</StatusPill>
            <h2>Citações mockadas</h2>
          </div>
          <span>{searchState}</span>
        </div>
        {searchState === "loading" && <div className="apoema-empty-state">Pesquisando no backend...</div>}
        {searchState === "empty" && <div className="apoema-empty-state"><strong>Nenhum resultado ainda</strong><p>Execute uma busca para ver citações determinísticas.</p></div>}
        {(searchState === "unauthorized" || searchState === "unavailable" || searchState === "error") && <div className="apoema-empty-state"><strong>Busca indisponível</strong><p>O backend não retornou resultados válidos.</p></div>}
        {results.length > 0 && (
          <div className="apoema-card-list">
            {results.map((item) => (
              <article key={item.document.document_id} className="apoema-stub-card">
                <div className="apoema-card-headline">
                  <BookOpen size={16} />
                  <strong>{item.document.title}</strong>
                  <StatusPill tone="warning">score {item.score}</StatusPill>
                </div>
                <p>{item.document.summary}</p>
                <small>Collection {item.document.collection} · Fonte mock: {item.document.citation}</small>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="apoema-stub-grid">
        <article className="apoema-panel">
          <StatusPill tone="info">Contexto de curso</StatusPill>
          <h2>{courseContext?.title ?? "Contexto controlado"}</h2>
          <p>{courseContext?.summary ?? "Contexto de curso exemplo indisponível no momento."}</p>
          {courseContext && <small>Público: {courseContext.audience} · {formatDate(courseContext.updated_at)}</small>}
        </article>
        <article className="apoema-panel">
          <StatusPill tone="warning">Auditoria recente</StatusPill>
          <div className="apoema-card-list">
            {auditEntries.length === 0 && <div className="apoema-empty-state"><strong>Sem eventos visíveis</strong><p>Auditoria pode exigir perfil ADMIN/MANAGER.</p></div>}
            {auditEntries.map((entry) => (
              <div key={entry.event_id} className="apoema-stub-card">
                <strong>{entry.event_type}</strong>
                <span>{entry.result}</span>
                <small>{entry.actor_role} · {formatDate(entry.occurred_at)}</small>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
