import type {
  ApoemaActivity,
  ApoemaAsset,
  ApoemaCommand,
  ApoemaConversation,
  ApoemaIntegration,
  ApoemaMessage,
  ApoemaMetric,
  ApoemaPreference
} from "./types";

export const apoemaMetrics: ApoemaMetric[] = [
  {
    label: "Ativos gerenciados",
    value: "12.842",
    delta: "+8,4%",
    tone: "positive",
    hint: "Inventário consolidado e classificado"
  },
  {
    label: "Automação executada",
    value: "1.256",
    delta: "+14,2%",
    tone: "positive",
    hint: "Rotinas N2 operando em lote"
  },
  {
    label: "Conformidade operacional",
    value: "98%",
    delta: "+3,1%",
    tone: "positive",
    hint: "Regras de segurança e qualidade"
  },
  {
    label: "Chamados em observação",
    value: "348",
    delta: "−12,7%",
    tone: "neutral",
    hint: "Fila de análise e tratativas"
  }
];

export const apoemaCommands: ApoemaCommand[] = [
  {
    title: "Importar inventário",
    description: "CSV, XLSX e integrações mockadas com validação em camadas.",
    action: "Abrir pipeline",
    icon: "folder-input"
  },
  {
    title: "Gerar macro",
    description: "Macros ITIL com placeholders, auditoria e cópia assistida.",
    action: "Abrir macros",
    icon: "clipboard-list"
  },
  {
    title: "Sincronizar CMDB",
    description: "Fluxo orquestrado para visão unificada de ativos e vínculos.",
    action: "Sincronizar agora",
    icon: "refresh-cw"
  }
];

export const apoemaActivities: ApoemaActivity[] = [
  {
    time: "09:32",
    title: "Inventário consolidado",
    detail: "7.120 ativos reconciliados com sucesso no lote do dia.",
    tone: "success"
  },
  {
    time: "09:18",
    title: "Macro gerada e copiada",
    detail: "Fluxo pós-movimentação permaneceu visível para conferência.",
    tone: "info"
  },
  {
    time: "08:47",
    title: "Regra de compliance revisada",
    detail: "Categoria de software crítico marcada para revisão manual.",
    tone: "warning"
  }
];

export const apoemaAssets: ApoemaAsset[] = [
  {
    id: "apo-1204",
    name: "NB-OPS-014",
    category: "Notebook",
    owner: "N2 / Infra",
    location: "Campus São Paulo",
    status: "healthy",
    lastSeen: "há 7 min",
    score: 98
  },
  {
    id: "apo-2208",
    name: "SRV-CMDB-02",
    category: "Servidor",
    owner: "Plataforma",
    location: "Datacenter Norte",
    status: "review",
    lastSeen: "há 31 min",
    score: 84
  },
  {
    id: "apo-3311",
    name: "PRN-ADM-05",
    category: "Impressora",
    owner: "Facilities",
    location: "Bloco B",
    status: "maintenance",
    lastSeen: "há 2 h",
    score: 71
  },
  {
    id: "apo-4427",
    name: "VDI-SUP-19",
    category: "Virtual Desktop",
    owner: "Service Desk",
    location: "Cloud Hub",
    status: "offline",
    lastSeen: "há 18 h",
    score: 52
  }
];

export const apoemaIntegrations: ApoemaIntegration[] = [
  {
    name: "CMDB",
    description: "Adapter mockado para inventário e relacionamentos.",
    status: "live",
    lastSync: "09:32",
    coverage: "96%"
  },
  {
    name: "ITSM",
    description: "Rotas assistidas para incidentes, tarefas e SLAs.",
    status: "mock",
    lastSync: "08:58",
    coverage: "83%"
  },
  {
    name: "Knowledge Base",
    description: "Pesquisa operacional e sugestões de ação contextual.",
    status: "live",
    lastSync: "agora",
    coverage: "91%"
  },
  {
    name: "Identity",
    description: "Perfil, permissões e contexto de operador.",
    status: "warning",
    lastSync: "há 5 min",
    coverage: "78%"
  }
];

export const apoemaPreferences: ApoemaPreference[] = [
  {
    label: "Copiar macro após movimentação",
    description: "Mantém o foco operacional no fluxo pós-aplicação.",
    enabled: true
  },
  {
    label: "Alertar arquivos sensíveis no chat",
    description: "Sinaliza .env, tokens e bancos locais antes de anexar.",
    enabled: true
  },
  {
    label: "Compactar layout em telas menores",
    description: "Preserva legibilidade em mobile sem sacrificar densidade.",
    enabled: true
  }
];

export const apoemaConversations: ApoemaConversation[] = [
  {
    id: "apo-conv-1",
    title: "Ativos com vencimento",
    subject: "Expiração em 30 dias",
    updatedAt: "09:35"
  },
  {
    id: "apo-conv-2",
    title: "Plano de importação",
    subject: "Lansweeper + macros",
    updatedAt: "08:51"
  },
  {
    id: "apo-conv-3",
    title: "Revisão de SLA",
    subject: "Chamados críticos",
    updatedAt: "Ontem"
  }
];

export const apoemaInitialMessages: ApoemaMessage[] = [
  {
    id: "apo-msg-1",
    role: "assistant",
    content:
      "Olá. Posso ajudar com inventário, movimentação, macros ITIL, integrações mockadas e leitura operacional de contexto.",
    time: "09:30"
  },
  {
    id: "apo-msg-2",
    role: "user",
    content: "Liste os ativos com risco de revisão e explique a prioridade.",
    time: "09:31"
  },
  {
    id: "apo-msg-3",
    role: "assistant",
    content:
      "Encontrei 3 ativos com revisão sugerida. O servidor SRV-CMDB-02 lidera por divergência de sincronização; a impressora PRN-ADM-05 pede validação física; o VDI-SUP-19 está sem heartbeat recente.",
    time: "09:32"
  }
];

export const apoemaQuickIdeas = [
  "Gerar resumo de ativos com divergências",
  "Preparar macro para movimentação segura",
  "Simular importação com validação de placeholders",
  "Revisar integrações e cobertura operacional"
];
