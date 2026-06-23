export type ThemeMode = "light" | "dark" | "auto";

export type ResolvedTheme = "light" | "dark";

export interface ApoemaMetric {
  label: string;
  value: string;
  delta: string;
  tone: "positive" | "neutral" | "alert";
  hint: string;
}

export interface ApoemaCommand {
  title: string;
  description: string;
  action: string;
  icon: string;
}

export interface ApoemaActivity {
  time: string;
  title: string;
  detail: string;
  tone: "info" | "success" | "warning";
}

export interface ApoemaAsset {
  id: string;
  name: string;
  category: string;
  owner: string;
  location: string;
  status: "healthy" | "review" | "maintenance" | "offline";
  lastSeen: string;
  score: number;
}

export interface ApoemaIntegration {
  name: string;
  description: string;
  status: "live" | "mock" | "warning";
  lastSync: string;
  coverage: string;
}

export interface ApoemaPreference {
  label: string;
  description: string;
  enabled: boolean;
}

export interface ApoemaConversation {
  id: string;
  title: string;
  subject: string;
  updatedAt: string;
}

export interface ApoemaAttachment {
  id: string;
  name: string;
  size: string;
  sizeBytes: number;
  mimeType: string;
  kind: "text" | "spreadsheet" | "pdf" | "image" | "script" | "log" | "unknown";
  sensitive?: boolean;
}

export interface ApoemaMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  time: string;
  attachments?: ApoemaAttachment[];
  source?: "live" | "fallback";
}

export type ApoemaProviderId = "mock" | "ollama" | "hermes";
export type ApoemaProviderStatus = "online" | "offline" | "error" | "unconfigured";
export type ApoemaChatStatus = "ok" | "offline" | "error" | "unconfigured";
export type ApoemaProviderLoadState = "loading" | "ready" | "fallback" | "error";
export type ApoemaApiErrorKind =
  | "auth_required"
  | "forbidden"
  | "rate_limited"
  | "validation_error"
  | "backend_error"
  | "network_unavailable"
  | "unknown_api_error";

export class ApoemaApiError extends Error {
  readonly kind: ApoemaApiErrorKind;
  readonly status?: number;
  readonly details?: unknown;

  constructor(message: string, kind: ApoemaApiErrorKind, status?: number, details?: unknown) {
    super(message);
    this.name = "ApoemaApiError";
    this.kind = kind;
    this.status = status;
    this.details = details;
  }
}

export type ApoemaProviderLoadResult =
  | {
      kind: "online";
      providers: ApoemaProviderOption[];
    }
  | {
      kind: "fallback";
      providers: ApoemaProviderOption[];
      offline: true;
      notice: string;
    };

export type ApoemaChatMessageResult =
  | {
      kind: "online";
      response: ApoemaChatResponse;
    }
  | {
      kind: "fallback";
      response: ApoemaChatResponse;
      offline: true;
      notice: string;
    };

export interface ApoemaProviderOption {
  id: ApoemaProviderId;
  label: string;
  status: ApoemaProviderStatus;
  models: string[];
  default_model: string;
}

export interface ApoemaChatAttachmentMeta {
  id: string;
  name: string;
  mime_type: string;
  size: number;
  kind: "text" | "spreadsheet" | "pdf" | "image" | "script" | "log" | "unknown";
  sensitive: boolean;
}

export interface ApoemaChatContext {
  route: "apoema-chat";
  source: "apoema-preview";
}

export interface ApoemaChatRequest {
  conversation_id: string | null;
  provider: ApoemaProviderId;
  model: string;
  message: string;
  mode: string;
  attachments: ApoemaChatAttachmentMeta[];
  context: ApoemaChatContext;
}

export interface ApoemaChatUsage {
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
}

export interface ApoemaChatResponse {
  conversation_id: string;
  message_id: string;
  provider: ApoemaProviderId;
  model: string;
  status: ApoemaChatStatus;
  content: string;
  created_at: string;
  usage: ApoemaChatUsage;
  error: string | null;
}
