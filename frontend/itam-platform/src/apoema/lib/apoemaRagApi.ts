import { ApoemaApiError } from "../types";
import type { ApoemaApiErrorKind } from "../types";

const API_BASE = "/api/v1";

export interface ApoemaRagCollection {
  id: string;
  label: string;
  description: string;
  document_count: number;
  tool_names: string[];
  updated_at: string;
}

export interface ApoemaRagDocument {
  document_id: string;
  collection: string;
  title: string;
  summary: string;
  citation: string;
  content: string;
  tags: string[];
  updated_at: string;
}

export interface ApoemaRagSearchResult {
  document: ApoemaRagDocument;
  score: number;
  matched_terms: string[];
}

export interface ApoemaRagSearchResponse {
  query: string;
  collections: string[];
  limit: number;
  total: number;
  items: ApoemaRagSearchResult[];
}

export interface ApoemaRagCourseContext {
  course_id: string;
  collection: string;
  title: string;
  summary: string;
  audience: string;
  key_documents: string[];
  recommendations: string[];
  updated_at: string;
}

export interface ApoemaRagAuditEntry {
  event_id: string;
  event_type: string;
  actor_role: string;
  collection: string | null;
  document_id: string | null;
  course_id: string | null;
  result: string;
  occurred_at: string;
  details: Record<string, unknown>;
}

export interface ApoemaRagAuditRecentResponse {
  items: ApoemaRagAuditEntry[];
  total: number;
}

function classifyStatus(status: number): ApoemaApiErrorKind {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 422) return "validation_error";
  if (status >= 500 && status < 600) return "backend_error";
  return "unknown_api_error";
}

function extractMessage(details: unknown, status: number): string {
  if (details && typeof details === "object" && "detail" in details) {
    const detail = (details as { detail?: unknown }).detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return `API ${status}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("content-type")) headers.set("content-type", "application/json");
  if (token) headers.set("authorization", `Bearer ${token}`);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: init.credentials ?? "include",
      headers,
    });

    if (!response.ok) {
      const rawText = await response.text().catch(() => "");
      let details: unknown = rawText || null;
      if (rawText.trim() && (response.headers.get("content-type") ?? "").includes("application/json")) {
        try {
          details = JSON.parse(rawText) as unknown;
        } catch {
          details = rawText;
        }
      }
      throw new ApoemaApiError(extractMessage(details, response.status), classifyStatus(response.status), response.status, details);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApoemaApiError) throw error;
    throw new ApoemaApiError("Backend indisponível por falha de rede.", "network_unavailable", undefined, error);
  }
}

export function listRagCollections(token?: string | null) {
  return requestJson<ApoemaRagCollection[]>("/rag/collections", {}, token);
}

export function searchRag(query: string, collections: string[], token?: string | null) {
  return requestJson<ApoemaRagSearchResponse>(
    "/rag/search",
    {
      method: "POST",
      body: JSON.stringify({ query, collections, limit: 5 }),
    },
    token,
  );
}

export function getRagDocument(documentId: string, token?: string | null) {
  return requestJson<ApoemaRagDocument>(`/rag/documents/${encodeURIComponent(documentId)}`, {}, token);
}

export function getRagCourseContext(courseId: string, token?: string | null) {
  return requestJson<ApoemaRagCourseContext>(`/rag/course-context/${encodeURIComponent(courseId)}`, {}, token);
}

export function getRagRecentAudit(token?: string | null) {
  return requestJson<ApoemaRagAuditRecentResponse>("/rag/audit/recent?limit=8", {}, token);
}
