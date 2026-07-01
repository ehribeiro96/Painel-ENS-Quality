import { ApoemaApiError } from "../types";
import type {
  ApoemaApiErrorKind,
  DesignerAdjustItemRequest,
  DesignerBannerJsonRequest,
  DesignerCancelResponse,
  DesignerFormOptions,
  DesignerHealth,
  DesignerJob,
  DesignerRefreshItemUrlRequest,
  DesignerRefreshItemUrlResponse,
  DesignerTemplate,
} from "../types";

const API_BASE = "/api/v1";

export interface DesignerTemplatesResponse {
  items: DesignerTemplate[];
  total: number;
}

function classifyStatus(status: number): ApoemaApiErrorKind {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 409) return "conflict";
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
  if (typeof value === "object" && value && "message" in value && typeof (value as { message?: unknown }).message === "string") {
    return (value as { message: string }).message;
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function errorMessage(details: unknown, status: number): string {
  if (details && typeof details === "object" && "detail" in details) {
    const detail = normalizeDetail((details as { detail?: unknown }).detail);
    if (detail) {
      return detail;
    }
  }
  const fallback = normalizeDetail(details);
  return fallback || `API ${status}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
  if (token) {
    headers.set("authorization", `Bearer ${token}`);
  }

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

    if (response.status === 204) {
      return undefined as T;
    }

    const contentType = response.headers.get("content-type") ?? "";
    if (!contentType.includes("application/json")) {
      return (await response.text()) as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApoemaApiError) {
      throw error;
    }
    throw new ApoemaApiError("Falha de rede ao acessar o Designer.", "network_unavailable", undefined, error);
  }
}

export function getDesignerHealth(token?: string | null) {
  return requestJson<DesignerHealth>("/designer/health", {}, token);
}

export function getDesignerTemplates(token?: string | null) {
  return requestJson<DesignerTemplatesResponse>("/designer/templates", {}, token);
}

export const listDesignerTemplates = getDesignerTemplates;

export function getDesignerFormOptions(token?: string | null) {
  return requestJson<DesignerFormOptions>("/designer/form-options", {}, token);
}

export function createDesignerBannerJson(payload: DesignerBannerJsonRequest, token?: string | null) {
  return requestJson<DesignerJob>(
    "/designer/banners/json",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function getDesignerJob(jobId: string, token?: string | null) {
  // "/designer/jobs/${encodeURIComponent(jobId)}"
  return requestJson<DesignerJob>(`/designer/jobs/${encodeURIComponent(jobId)}`, {}, token);
}

export function adjustDesignerJobItem(jobId: string, itemId: string, payload: DesignerAdjustItemRequest, token?: string | null) {
  // "/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/adjust"
  return requestJson<DesignerJob>(
    `/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/adjust`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function refreshDesignerJobItemUrl(jobId: string, itemId: string, payload: DesignerRefreshItemUrlRequest = {}, token?: string | null) {
  // "/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/refresh-url"
  return requestJson<DesignerRefreshItemUrlResponse>(
    `/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/refresh-url`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function cancelDesignerJob(jobId: string, token?: string | null) {
  // "/designer/jobs/${encodeURIComponent(jobId)}/cancel"
  return requestJson<DesignerCancelResponse>(
    `/designer/jobs/${encodeURIComponent(jobId)}/cancel`,
    { method: "POST" },
    token,
  );
}
