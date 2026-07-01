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

export type RagCollectionId = "courses" | "institutional" | "marketing" | "insights";

export type DesignerChannel = string;
export type DesignerKv =
  | "graduacao"
  | "imersoes"
  | "institucional"
  | "pos"
  | "qualificacoes"
  | "tudo-sobre-seguros";
export type DesignerGenerationMode = "peca_unica" | "enxoval";
export type DesignerJobStatus = "queued" | "running" | "completed" | "failed" | "cancelled" | "expired";
export type DesignerJobItemStatus = "queued" | "running" | "completed" | "failed" | "cancelled";
export type DesignerErrorCode = ApoemaApiErrorKind;
export type DesignerApiError = ApoemaApiError;

export interface DesignerHealth {
  status: string;
  service: string;
  mode: string;
  deterministic: boolean;
  provider_real_enabled: boolean;
  template_count: number;
  job_count: number;
  note: string;
}

export interface DesignerTemplate {
  template_id: string;
  canal: DesignerChannel;
  kv: DesignerKv;
  label: string;
  description: string;
  mode_options: DesignerGenerationMode[];
  box2_allowed: boolean;
  persona_image_allowed: boolean;
  prompt_budget: number;
  copy_budget: number;
}

export interface DesignerFormOptions {
  channels: DesignerChannel[];
  kvs: DesignerKv[];
  modes: DesignerGenerationMode[];
  template_ids: string[];
  supports_box2: boolean;
  supports_persona_image: boolean;
  max_prompt_length: number;
  max_copy_length: number;
  max_items_per_job: number;
}

export interface DesignerBannerJsonRequest {
  template_id: string;
  canal: DesignerChannel;
  kv: DesignerKv;
  modo_geracao: DesignerGenerationMode;
  prompt: string;
  copy?: string;
  box2?: string;
  persona_image?: string;
  item_count: number;
}

export interface DesignerAdjustItemRequest {
  adjustment_prompt: string;
  copy?: string;
  box2?: string;
}

export interface DesignerRefreshItemUrlRequest {
  reason?: string;
}

export interface DesignerErrorShape {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface DesignerJobItem {
  item_id: string;
  template_id: string;
  title: string;
  status: DesignerJobItemStatus;
  copy_preview: string;
  prompt_preview: string;
  result_note: string;
  adjusted_count: number;
  refresh_count: number;
  created_at: string;
  updated_at: string;
  error?: DesignerErrorShape | null;
}

export interface DesignerJob {
  job_id: string;
  owner_user_id: string;
  status: DesignerJobStatus;
  created_at: string;
  updated_at: string;
  template_id: string;
  canal: DesignerChannel;
  kv: DesignerKv;
  modo_geracao: DesignerGenerationMode;
  box2: string | null;
  persona_image_present: boolean;
  prompt_preview: string;
  copy_preview: string;
  progress: number;
  items: DesignerJobItem[];
  summary: string;
  error?: DesignerErrorShape | null;
}

export interface DesignerCancelResponse {
  job_id: string;
  status: DesignerJobStatus;
  cancelled_at: string;
  items_cancelled: number;
  message: string;
}

export type DesignerRefreshItemUrlResponse = DesignerJob;

export type AiChatProviderId = ApoemaProviderId;
export type AiChatProviderStatus = ApoemaProviderStatus;
export type AiChatErrorCode = ApoemaApiErrorKind;
export type AiChatMessageRole = "system" | "user" | "assistant" | "tool";

export interface AiChatProvider {
  id: AiChatProviderId;
  label: string;
  status: AiChatProviderStatus;
  models: string[];
  default_model: string;
}

export interface AiChatHealth {
  enabled: boolean;
  provider?: string;
  configured?: boolean;
  status?: string;
  detail?: string | null;
  model?: string | null;
  [key: string]: unknown;
}

export interface AiChatMessage {
  id: string;
  conversation_id: string;
  role: AiChatMessageRole;
  content: string;
  provider: string | null;
  model: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AiChatConversation {
  id: string;
  user_id: string;
  title: string | null;
  provider: string;
  model: string | null;
  system_prompt_version: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  messages?: AiChatMessage[];
}

export interface AiChatConversationCreate {
  title?: string | null;
  message?: string | null;
  mode?: string | null;
}

export interface AiChatMessageCreate {
  content: string;
  mode?: string | null;
}

export interface AiChatSendMessageRequest {
  conversation_id: string | null;
  provider: AiChatProviderId;
  model: string;
  message: string;
  mode: string;
}

export interface AiChatSendMessageResponse {
  conversation_id: string;
  message_id: string;
  provider: AiChatProviderId;
  model: string;
  status: ApoemaChatStatus;
  content: string;
  created_at: string;
  usage: ApoemaChatUsage;
  error: string | null;
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
  | "not_found"
  | "conflict"
  | "expired"
  | "rate_limited"
  | "validation_error"
  | "backend_error"
  | "network_unavailable"
  | "unknown_api_error";

export type RagErrorCode = ApoemaApiErrorKind;

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

export class AiChatApiError extends ApoemaApiError {}

export class RagApiError extends ApoemaApiError {}

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
