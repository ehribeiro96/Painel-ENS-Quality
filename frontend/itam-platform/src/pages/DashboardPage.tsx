import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Archive, Box, Link2, Monitor, PackageCheck, Upload, Users, Wrench } from "lucide-react";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelHero } from "@/components/brand/SentinelHero";
import { AlertBlock, EmptyState, LoadingBlock } from "@/components/StateBlocks";
import {
  AgentOrbitIcon,
  ConflictSplitIcon,
  HermesCoreIcon,
  PackageChipIcon,
  SettingsCircuitIcon,
  TransferCircuitIcon
} from "@/components/icons/HermesIcons";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Asset, Page } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  IN_USE: "Em uso",
  STOCK: "Em estoque",
  MAINTENANCE: "Em manutenção",
  DEFECTIVE: "Defeituoso",
  DISCARDED: "Para descarte",
  RESERVED: "Reservado",
  CONFIG_PENDING: "Configuração pendente"
};

const TYPE_LABELS: Record<string, string> = {
  NOTEBOOK: "Notebook",
  DESKTOP: "Desktop",
  MONITOR: "Monitor",
  DOCK: "Dock",
  MOBILE: "Mobile",
  PRINTER: "Impressora",
  PERIPHERAL: "Periférico",
  OTHER: "Outro"
};

function countBy(items: Asset[], getter: (asset: Asset) => string | null | undefined) {
  const counts = new Map<string, number>();
  for (const item of items) {
    const key = getter(item) || "Não informado";
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
}

type DashboardStatusItem = {
  status: string;
  count: number;
};

function normalizeStatusItem(item: unknown): DashboardStatusItem {
  const record = item && typeof item === "object" ? item as Record<string, unknown> : {};
  const rawStatus = record.status ?? record.name ?? "Não informado";
  const rawCount = record.count ?? record.value ?? 0;
  const count = typeof rawCount === "number" ? rawCount : Number(rawCount);

  return {
    status: String(rawStatus || "Não informado"),
    count: Number.isFinite(count) ? count : 0
  };
}

function formatStatus(status: string | null | undefined) {
  const safeStatus = status || "Não informado";
  return STATUS_LABELS[safeStatus] ?? safeStatus.replaceAll("_", " ").toLowerCase();
}

function formatAssetType(assetType: string) {
  return TYPE_LABELS[assetType] ?? assetType.replaceAll("_", " ").toLowerCase();
}

function percent(value: number, total: number) {
  if (!total) {
    return 0;
  }
  return Math.round((value / total) * 100);
}

export function DashboardPage() {
  const { token } = useAuth();
  const summaryQuery = useQuery({ queryKey: ["dashboard-summary"], enabled: Boolean(token), queryFn: () => api.dashboardSummary(token as string) });
  const statusQuery = useQuery({ queryKey: ["dashboard-status"], enabled: Boolean(token), queryFn: () => api.assetsByStatus(token as string) });
  const assetsQuery = useQuery({ queryKey: ["dashboard-assets-overview"], enabled: Boolean(token), queryFn: () => api.assets(token as string, "?page_size=200&sort_by=updated_at&sort_order=desc") });

  const summary = summaryQuery.data ?? {};
  const assets = (assetsQuery.data as Page<Asset> | undefined)?.items ?? [];
  const activeUsers = new Set(assets.map((asset) => asset.current_user_id).filter(Boolean)).size;
  const assignments = assets.filter((asset) => asset.current_user_id).length;
  const unassignedAssets = assets.filter((asset) => !asset.current_user_id && asset.status !== "DISCARDED").length;
  const byStatus = (statusQuery.data ?? []).map(normalizeStatusItem);
  const defective = byStatus.find((item) => item.status === "DEFECTIVE")?.count ?? 0;
  const discarded = byStatus.find((item) => item.status === "DISCARDED")?.count ?? 0;
  const maintenance = summary.maintenance ?? byStatus.find((item) => item.status === "MAINTENANCE")?.count ?? 0;
  const stock = summary.stock ?? byStatus.find((item) => item.status === "STOCK")?.count ?? 0;
  const totalAssets = summary.total_assets ?? assetsQuery.data?.total ?? assets.length;
  const byUnit = countBy(assets, (asset) => asset.location?.split("-")[0]?.trim());
  const byType = countBy(assets, (asset) => asset.asset_type).slice(0, 8);
  const statusTotal = byStatus.reduce((total, item) => total + item.count, 0) || totalAssets;
  const maxUnitCount = Math.max(...byUnit.map(([, count]) => count), 1);
  const maxTypeCount = Math.max(...byType.map(([, count]) => count), 1);
  const hasAnyData = totalAssets > 0 || assets.length > 0 || byStatus.length > 0;
  const isLoading = summaryQuery.isLoading || assetsQuery.isLoading || statusQuery.isLoading;
  const isError = summaryQuery.isError || assetsQuery.isError || statusQuery.isError;

  const metrics = [
    { label: "Total de ativos", value: totalAssets, description: "Base operacional cadastrada", icon: HermesCoreIcon, tone: "blue", badge: "CMDB" },
    { label: "Colaboradores ativos", value: activeUsers, description: "Com ativo vinculado na amostra", icon: AgentOrbitIcon, tone: "green", badge: "Uso" },
    { label: "Vínculos vigentes", value: assignments, description: "Ativos atualmente atribuídos", icon: TransferCircuitIcon, tone: "purple", badge: `${percent(assignments, Math.max(assets.length, 1))}%` },
    { label: "Em estoque", value: stock, description: "Disponíveis para operação", icon: PackageChipIcon, tone: "teal", badge: "Estoque" },
    { label: "Em manutenção", value: maintenance, description: "Exigem acompanhamento técnico", icon: SettingsCircuitIcon, tone: "amber", badge: maintenance > 0 ? "Atenção" : "OK" },
    { label: "Para descarte", value: discarded, description: "Itens fora do ciclo operacional", icon: ConflictSplitIcon, tone: "red", badge: discarded > 0 ? "Revisar" : "OK" }
  ];

  const recommendations = [
    {
      title: "Ativos sem usuário",
      value: unassignedAssets,
      message: unassignedAssets > 0 ? "Revise estoque, reserva ou pendências de vínculo." : "Nenhum item sem usuário na amostra atual.",
      tone: unassignedAssets > 0 ? "warning" : "success",
      href: "/assets"
    },
    {
      title: "Manutenção",
      value: maintenance,
      message: maintenance > 0 ? "Acompanhe reparos e próximos responsáveis." : "Sem ativos em manutenção no resumo.",
      tone: maintenance > 0 ? "warning" : "success",
      href: "/assets"
    },
    {
      title: "Defeituosos",
      value: defective,
      message: defective > 0 ? "Priorize diagnóstico, troca ou descarte técnico." : "Sem ativos defeituosos informados.",
      tone: defective > 0 ? "danger" : "success",
      href: "/assets"
    },
    {
      title: "Pendências operacionais",
      value: byStatus.find((item) => item.status === "CONFIG_PENDING")?.count ?? 0,
      message: (byStatus.find((item) => item.status === "CONFIG_PENDING")?.count ?? 0) > 0 ? "Finalize configuração antes de movimentar para uso." : "Sem configuração pendente no status atual.",
      tone: (byStatus.find((item) => item.status === "CONFIG_PENDING")?.count ?? 0) > 0 ? "warning" : "success",
      href: "/assets"
    }
  ];

  return (
    <>
      <SentinelHero
        actions={(
          <nav className="dashboard-actions" aria-label="Ações rápidas do dashboard">
            <Link className="button secondary" to="/assets">Inventário</Link>
            <Link className="button secondary" to="/assignments">Movimentações</Link>
            <Link className="button" to="/imports">Importação Lansweeper</Link>
          </nav>
        )}
        chips={(
          <>
            <HermesStatusPill state="Online">Agente local</HermesStatusPill>
            <HermesStatusPill state="Auditável">Inventário auditável</HermesStatusPill>
            <HermesStatusPill state="Em revisão">Macro e movimentação</HermesStatusPill>
          </>
        )}
        description="Visão operacional de inventário, vínculos, pendências e auditoria da infraestrutura."
        eyebrow="Centro de Comando"
        subtitle="Guardião local da infraestrutura"
        title="Centro de Comando"
      />

      {isError ? (
        <AlertBlock tone="danger">
          <strong>Não foi possível carregar o dashboard.</strong>
          <p>Atualize a página. Se continuar falhando, verifique autenticação, migrações e logs do backend.</p>
        </AlertBlock>
      ) : null}

      {isLoading ? <LoadingBlock label="Carregando indicadores do dashboard..." /> : null}

      {!isLoading && !isError && !hasAnyData ? (
        <EmptyState
          title="Ainda não há dados para o dashboard."
          description="Importe ativos ou cadastre registros para alimentar os indicadores operacionais."
        >
          <Link className="button" to="/imports">Importar dados</Link>
          <Link className="button secondary" to="/assets">Cadastrar ativo</Link>
        </EmptyState>
      ) : null}

      <section className="dashboard-grid dashboard-metrics" aria-label="Métricas principais">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className="card metric-card" key={metric.label}>
              <div className="metric-card-header">
                <span className={`metric-icon tone-${metric.tone}`}><Icon size={18} aria-hidden="true" /></span>
                <HermesStatusPill state={metric.tone === "red" ? "Conflito" : metric.tone === "amber" ? "Pendente" : metric.tone === "green" ? "Validado" : "Auditável"}>{metric.badge}</HermesStatusPill>
              </div>
              <strong className="metric-value">{metric.value}</strong>
              <span className="metric-label">{metric.label}</span>
              <p className="metric-description">{metric.description}</p>
            </article>
          );
        })}
      </section>

      <section className="grid dashboard-panels">
        <article className="card chart-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Ativos por status</h2>
              <p className="card-description">Distribuição real retornada pelo backend.</p>
            </div>
            <span className="badge neutral">{statusTotal} ativos</span>
          </div>
          {byStatus.length ? (
            <div className="distribution-list">
              {byStatus.map((item) => {
                const itemPercent = percent(item.count, statusTotal);
                return (
                  <div className="distribution-item" key={item.status}>
                    <div className="distribution-item-line">
                      <span title={formatStatus(item.status)}>{formatStatus(item.status)}</span>
                      <strong>{item.count}</strong>
                    </div>
                    <div className="distribution-bar" aria-label={`${formatStatus(item.status)}: ${itemPercent}%`}>
                      <span style={{ width: `${itemPercent}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState title="Sem status para exibir." description="Os totais por status ainda não foram retornados pelo backend." />
          )}
        </article>

        <article className="card chart-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Ativos por unidade</h2>
              <p className="card-description">Agrupamento por prefixo da localização nos ativos carregados.</p>
            </div>
          </div>
          {byUnit.length ? (
            <div className="distribution-list">
              {byUnit.slice(0, 6).map(([name, value]) => {
                const itemPercent = percent(value, maxUnitCount);
                return (
                  <div className="distribution-item" key={name}>
                    <div className="distribution-item-line">
                      <span title={name}>{name}</span>
                      <strong>{value}</strong>
                    </div>
                    <div className="distribution-bar" aria-label={`${name}: ${value} ativos`}>
                      <span style={{ width: `${itemPercent}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState title="Sem unidades identificadas." description="Preencha localização nos ativos para acompanhar a distribuição por unidade." />
          )}
        </article>

        <article className="card chart-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Top tipos de ativo</h2>
              <p className="card-description">Tipos mais frequentes na amostra recente.</p>
            </div>
          </div>
          {byType.length ? (
            <div className="distribution-list">
              {byType.map(([name, value]) => {
                const itemPercent = percent(value, maxTypeCount);
                return (
                  <div className="distribution-item" key={name}>
                    <div className="distribution-item-line">
                      <span title={formatAssetType(name)}>{formatAssetType(name)}</span>
                      <strong>{value}</strong>
                    </div>
                    <div className="distribution-bar" aria-label={`${formatAssetType(name)}: ${value} ativos`}>
                      <span style={{ width: `${itemPercent}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState title="Sem tipos para exibir." description="Cadastre ou importe ativos para montar o ranking de tipos." />
          )}
        </article>
      </section>

      <section className="card dashboard-recommendations">
        <div className="card-header">
          <div>
            <h2 className="card-title">Ações recomendadas</h2>
            <p className="card-description">Sinais derivados apenas dos contadores já carregados nesta página.</p>
          </div>
          <span className="badge neutral">Sem endpoint novo</span>
        </div>
        <div className="recommendation-list">
          {recommendations.map((item) => (
            <Link className={`recommendation-card ${item.tone}`} to={item.href} key={item.title}>
              <span className="recommendation-title">{item.title}</span>
              <strong>{item.value}</strong>
              <p>{item.message}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="quick-card-grid">
        <Link className="quick-card blue" to="/assets"><PackageCheck size={17} /> <span><strong>Gerenciar ativos</strong><small>Ver, filtrar e editar o inventário</small></span></Link>
        <Link className="quick-card green" to="/users"><Users size={17} /> <span><strong>Colaboradores</strong><small>Consultar vínculos por usuário</small></span></Link>
        <Link className="quick-card purple" to="/assignments"><Link2 size={17} /> <span><strong>Atribuições</strong><small>Histórico de vínculos e movimentações</small></span></Link>
        <Link className="quick-card amber" to="/imports"><Upload size={17} /> <span><strong>Importar Excel</strong><small>Atualizar dados via fluxo existente</small></span></Link>
      </section>
    </>
  );
}
