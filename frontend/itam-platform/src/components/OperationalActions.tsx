import { Archive, History, PackageCheck, Repeat2, Search } from "lucide-react";
import { Link } from "react-router-dom";

const actions = [
  { label: "Localizar ativo", icon: Search, href: "/assets" },
  { label: "Movimentar", icon: Repeat2, href: "/assets" },
  { label: "Enviar estoque", icon: PackageCheck, href: "/assets?status=STOCK" },
  { label: "Historico", icon: History, href: "/audit-logs" },
  { label: "Importar", icon: Archive, href: "/imports" }
];

export function OperationalActions() {
  return (
    <div className="quick-actions" aria-label="Acoes operacionais principais">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <Link className="icon-button" key={action.label} to={action.href} title={action.label}>
            <Icon size={18} aria-hidden />
            <span>{action.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
