import { ApoemaApiError } from "../types";
import type { ApoemaApiErrorKind } from "../types";

const API_BASE = "/api/v1";

export interface ApoemaArtifact {
  id: string;
  owner_user_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
  created_at: string;
  updated_at: string;
  download_count: number;
  deleted_at: string | null;
  deleted_by: string | null;
}

export interface ApoemaArtifactListResponse {
  items: ApoemaArtifact[];
  total: number;
}

export interface ApoemaArtifactDownloadUrlResponse {
  artifact_id: string;
  url: string;
  expires_at: string;
}

export interface ApoemaArtifactDeleteResponse {
  ok: boolean;
  artifact_id: string;
  deleted_at: string;
}

function classifyStatus(status: number): ApoemaApiErrorKind {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 422) return "validation_error";
  if (status >= 500 && status < 600) return "backend_error";
  return "unknown_api_error";
}

function normalizeDetail(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function errorMessage(details: unknown, status: number): string {
  if (details && typeof details === "object" && "detail" in details) {
    const detail = normalizeDetail((details as { detail?: unknown }).detail);
    if (detail) return detail;
  }
  return `API ${status}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
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
      throw new ApoemaApiError(errorMessage(details, response.status), classifyStatus(response.status), response.status, details);
    }

    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApoemaApiError) throw error;
    throw new ApoemaApiError("Backend indisponível por falha de rede.", "network_unavailable", undefined, error);
  }
}

export function listArtifacts(token?: string | null) {
  return requestJson<ApoemaArtifactListResponse>("/artifacts", {}, token);
}

export function uploadArtifact(file: File, token?: string | null) {
  const body = new FormData();
  body.append("file", file);
  return requestJson<ApoemaArtifact>("/artifacts", { method: "POST", body }, token);
}

export function getArtifact(artifactId: string, token?: string | null) {
  return requestJson<ApoemaArtifact>(`/artifacts/${encodeURIComponent(artifactId)}`, {}, token);
}

export function getArtifactDownloadUrl(artifactId: string, token?: string | null) {
  return requestJson<ApoemaArtifactDownloadUrlResponse>(`/artifacts/${encodeURIComponent(artifactId)}/download-url`, {}, token);
}

export function deleteArtifact(artifactId: string, token?: string | null) {
  return requestJson<ApoemaArtifactDeleteResponse>(`/artifacts/${encodeURIComponent(artifactId)}`, { method: "DELETE" }, token);
}
