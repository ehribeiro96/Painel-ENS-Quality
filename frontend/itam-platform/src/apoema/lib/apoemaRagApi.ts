import { RagApiError } from "../types";
import type { RagCollectionId, RagErrorCode } from "../types";

const API_BASE = "/api/v1";

export interface RagCollection {
  id: RagCollectionId;
  label: string;
  description: string;
  document_count: number;
  tool_names: string[];
  updated_at: string;
}

export interface RagSearchRequest {
  query: string;
  collections?: RagCollectionId[];
  limit?: number;
}

export interface RagDocument {
  document_id: string;
  collection: RagCollectionId;
  title: string;
  summary: string;
  citation: string;
  content: string;
  tags: string[];
  updated_at: string;
}

export interface RagSearchResult {
  document: RagDocument;
  score: number;
  matched_terms: string[];
}

export interface RagSearchResponse {
  query: string;
  collections: RagCollectionId[];
  limit: number;
  total: number;
  items: RagSearchResult[];
}

export interface RagCourseContext {
  course_id: string;
  collection: RagCollectionId;
  title: string;
  summary: string;
  audience: string;
  key_documents: string[];
  recommendations: string[];
  updated_at: string;
}

export interface RagAuditEntry {
  event_id: string;
  event_type: string;
  actor_role: string;
  collection: RagCollectionId | null;
  document_id: string | null;
  course_id: string | null;
  result: string;
  occurred_at: string;
  details: Record<string, unknown>;
}

export interface RagAuditRecentResponse {
  items: RagAuditEntry[];
  total: number;
}

function classifyStatus(status: number): RagErrorCode {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 410) return "expired";
  if (status === 422) return "validation_error";
  if (status === 429) return "rate_limited";
  if (status >= 500 && status < 600) return "backend_error";
  return "unknown_api_error";
}

function normalizeDetail(value: unknown): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "string") {
    return value;
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function extractMessage(details: unknown, status: number): string {
  if (details && typeof details === "object" && "detail" in details) {
    const detail = normalizeDetail((details as { detail?: unknown }).detail);
    if (detail) return detail;
  }
  return `API ${status}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
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
      throw new RagApiError(extractMessage(details, response.status), classifyStatus(response.status), response.status, details);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof RagApiError) throw error;
    throw new RagApiError("Falha de rede ao consultar o RAG.", "network_unavailable", undefined, error);
  }
}

export function getRagCollections(token?: string | null) {
  return requestJson<RagCollection[]>("/rag/collections", {}, token);
}

export function listRagCollections(token?: string | null) {
  return getRagCollections(token);
}

export function searchRag(payload: RagSearchRequest, token?: string | null) {
  return requestJson<RagSearchResponse>(
    "/rag/search",
    {
      method: "POST",
      body: JSON.stringify({
        query: payload.query,
        collections: payload.collections ?? [],
        limit: payload.limit ?? 10,
      }),
    },
    token,
  );
}

export function getRagDocument(documentId: string, token?: string | null) {
  return requestJson<RagDocument>(`/rag/documents/${encodeURIComponent(documentId)}`, {}, token);
}

export function getRagCourseContext(courseId: string, token?: string | null) {
  return requestJson<RagCourseContext>(`/rag/course-context/${encodeURIComponent(courseId)}`, {}, token);
}

export function getRagAuditRecent(limit = 8, token?: string | null) {
  return requestJson<RagAuditRecentResponse>(`/rag/audit/recent?limit=${encodeURIComponent(String(limit))}`, {}, token);
}

export function getRagRecentAudit(token?: string | null) {
  return getRagAuditRecent(8, token);
}
