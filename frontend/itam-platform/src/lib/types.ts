export type AssetStatus = "IN_USE" | "STOCK" | "MAINTENANCE" | "DEFECTIVE" | "DISCARDED" | "RESERVED" | "CONFIG_PENDING";
export type AssetType = "NOTEBOOK" | "DESKTOP" | "MONITOR" | "DOCK" | "MOBILE" | "PRINTER" | "PERIPHERAL" | "OTHER";
export type UserStatus = "ACTIVE" | "INACTIVE" | "ON_LEAVE";
export type Role = "ADMIN" | "TECHNICIAN" | "VIEWER" | "MANAGER";

export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type Asset = {
  id: string;
  hostname: string | null;
  patrimony: string | null;
  serial: string | null;
  manufacturer: string | null;
  model: string | null;
  asset_type: AssetType;
  status: AssetStatus;
  location: string | null;
  operating_system: string | null;
  ip_address: string | null;
  last_login: string | null;
  notes: string | null;
  current_user_id: string | null;
  current_user?: {
    id: string;
    name: string;
    email: string;
  } | null;
  created_at: string;
  updated_at: string;
};

export type User = {
  id: string;
  name: string;
  email: string;
  job_title: string | null;
  department: string | null;
  business_unit: string | null;
  manager_name: string | null;
  phone: string | null;
  status: UserStatus;
  role: Role;
  source: string | null;
  source_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type ImportJob = {
  id: string;
  filename: string;
  source: string;
  status: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created_rows: number;
  updated_rows: number;
  skipped_rows: number;
  conflict_rows: number;
  failed_rows: number;
  report: Record<string, unknown>;
  created_at: string;
};

export type ImportStagingAsset = {
  id: string;
  job_id: string;
  row_number: number;
  raw_payload: Record<string, unknown>;
  normalized_payload: Record<string, unknown>;
  identity_type: string | null;
  identity_value: string | null;
  identity_confidence: string | null;
  decision: string;
  row_status: string;
  matched_asset_id: string | null;
  merge_action: string | null;
  issues: Array<Record<string, unknown>>;
};

export type ImportPreview = {
  job: ImportJob;
  columns: string[];
  detected_mapping: Record<string, string>;
  items: ImportStagingAsset[];
};

export type ImportConflict = {
  id: string;
  job_id: string;
  staging_asset_id: string | null;
  conflict_type: string;
  severity: string;
  details: Record<string, unknown>;
};

export type ImportValidationError = {
  id: string;
  job_id: string;
  staging_asset_id: string | null;
  row_number: number | null;
  field_name: string | null;
  error_code: string;
  message: string;
};

export type AuditLog = {
  id: string;
  actor_id: string | null;
  action: string;
  entity: string;
  entity_id: string | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  ip_address: string | null;
  request_id: string | null;
  correlation_id: string | null;
  source: string;
  created_at: string;
};

export type Movement = {
  id: string;
  asset_id: string;
  previous_user_id: string | null;
  new_user_id: string | null;
  previous_status: AssetStatus;
  new_status: AssetStatus;
  previous_location: string | null;
  new_location: string | null;
  responsible_id: string | null;
  justification: string;
  notes: string | null;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type SearchResult = {
  id: string;
  type: "asset" | "user";
  title: string;
  subtitle: string;
  href: string;
};

export type SearchResponse = {
  query: string;
  items: SearchResult[];
};

export type MacroTemplate = {
  id: string;
  name: string;
  slug: string;
  category: string;
  description: string | null;
  template_text: string;
  required_fields: string[];
  optional_fields: string[];
  context_type: string | null;
  source: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type MacroRenderResponse = {
  rendered_text: string;
  pending_fields: string[];
};

export type MacroGeneration = {
  id: string;
  template_id: string;
  context_type: string | null;
  context_id: string | null;
  rendered_text: string;
  input_values: Record<string, unknown>;
  generated_by: string | null;
  ticket_number: string | null;
  copied: boolean;
  copied_at: string | null;
  created_at: string;
};

export type MacroAutocompleteHint = {
  id: string;
  label: string;
  hint_type: string;
  source: string;
};

export type SuggestedMovementMacro = {
  movement_id: string;
  generation_id: string | null;
  template_id: string | null;
  template_name: string | null;
  rendered_text: string;
  pending_fields: string[];
  values: Record<string, unknown>;
};


export type AiChatRole = "system" | "user" | "assistant";
export type AiChatMode =
  | "general"
  | "fix_text"
  | "draft_ticket"
  | "update_ticket"
  | "resolution"
  | "summarize"
  | "improve_tone"
  | "service_macro"
  | "asset_guidance";

export type AiChatMessageCreate = {
  content: string;
  mode?: AiChatMode | null;
};

export type AiChatConversationCreate = {
  title?: string | null;
  message?: string | null;
  mode?: AiChatMode | null;
};

export type AiChatMessage = {
  id: string;
  conversation_id: string;
  role: AiChatRole;
  content: string;
  provider: string | null;
  model: string | null;
  created_at: string;
};

export type AiChatConversation = {
  id: string;
  user_id: string;
  title: string | null;
  provider: string;
  model: string | null;
  system_prompt_version: string;
  created_at: string;
  updated_at: string;
};

export type AiChatProviderHealth = {
  enabled: boolean;
  provider: string;
  configured: boolean;
  status: string;
  detail?: string;
  model?: string;
};

export type AiChatConversationDetail = AiChatConversation & {
  messages: AiChatMessage[];
};
