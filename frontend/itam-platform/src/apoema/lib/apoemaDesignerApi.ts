import { ApoemaApiError } from "../types";
import type { ApoemaApiErrorKind } from "../types";

const API_BASE = "/api/v1";

export interface ApoemaDesignerHealth {
  status: string;
  service: string;
  mode: string;
  deterministic: boolean;
  provider_real_enabled: boolean;
  template_count: number;
  job_count: number;
  note: string;
}

export interface ApoemaDesignerTemplate {
  template_id: string;
  canal: string;
  kv: string;
  label: string;
  description: string;
  mode_options: string[];
  box2_allowed: boolean;
  persona_image_allowed: boolean;
  prompt_budget: number;
  copy_budget: number;
}

export interface ApoemaDesignerTemplatesResponse {
  items: ApoemaDesignerTemplate[];
  total: number;
}

export interface ApoemaDesignerFormOptions {
  channels: string[];
  kvs: string[];
  modes: string[];
  template_ids: string[];
  supports_box2: boolean;
  supports_persona_image: boolean;
  max_prompt_length: number;
  max_copy_length: number;
  max_items_per_job: number;
}

export interface ApoemaDesignerJobItem {
  item_id: string;
  template_id: string;
  title: string;
  status: string;
  copy_preview: string;
  prompt_preview: string;
  result_note: string;
  adjusted_count: number;
  refresh_count: number;
  created_at: string;
  updated_at: string;
}

export interface ApoemaDesignerJob {
  job_id: string;
  owner_user_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  template_id: string;
  canal: string;
  kv: string;
  modo_geracao: string;
  box2: string | null;
  persona_image_present: boolean;
  prompt_preview: string;
  copy_preview: string;
  progress: number;
  items: ApoemaDesignerJobItem[];
  summary: string;
}

export interface ApoemaDesignerBannerJsonRequest {
  template_id: string;
  canal: string;
  kv: string;
  modo_geracao: string;
  prompt: string;
  copy?: string;
  box2?: string;
  item_count: number;
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
    if (detail && typeof detail === "object" && "message" in detail && typeof (detail as { message?: unknown }).message === "string") {
      return (detail as { message: string }).message;
    }
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

export function getDesignerHealth(token?: string | null) {
  return requestJson<ApoemaDesignerHealth>("/designer/health", {}, token);
}

export function listDesignerTemplates(token?: string | null) {
  return requestJson<ApoemaDesignerTemplatesResponse>("/designer/templates", {}, token);
}

export function getDesignerFormOptions(token?: string | null) {
  return requestJson<ApoemaDesignerFormOptions>("/designer/form-options", {}, token);
}

export function createDesignerBannerJob(payload: ApoemaDesignerBannerJsonRequest, token?: string | null) {
  return requestJson<ApoemaDesignerJob>(
    "/designer/banners/json",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function getDesignerJob(jobId: string, token?: string | null) {
  return requestJson<ApoemaDesignerJob>(`/designer/jobs/${encodeURIComponent(jobId)}`, {}, token);
}

export function adjustDesignerJobItem(jobId: string, itemId: string, token?: string | null) {
  return requestJson<ApoemaDesignerJob>(
    `/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/adjust`,
    { method: "POST", body: JSON.stringify({ adjustment_prompt: "Ajuste determinístico controlado pelo backend." }) },
    token,
  );
}

export function refreshDesignerJobItemUrl(jobId: string, itemId: string, token?: string | null) {
  return requestJson<ApoemaDesignerJob>(
    `/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/refresh-url`,
    { method: "POST", body: JSON.stringify({ reason: "Validação de stub Apoema M6B." }) },
    token,
  );
}

export function cancelDesignerJob(jobId: string, token?: string | null) {
  return requestJson<{ job_id: string; status: string; cancelled_at: string; items_cancelled: number; message: string }>(
    `/designer/jobs/${encodeURIComponent(jobId)}/cancel`,
    { method: "POST" },
    token,
  );
}
