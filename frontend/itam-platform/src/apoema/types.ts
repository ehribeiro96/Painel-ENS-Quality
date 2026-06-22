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
  kind: string;
  sensitive?: boolean;
}

export interface ApoemaMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  time: string;
  attachments?: ApoemaAttachment[];
}
