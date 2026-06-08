/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly ENABLE_AI_CHAT?: string;
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
