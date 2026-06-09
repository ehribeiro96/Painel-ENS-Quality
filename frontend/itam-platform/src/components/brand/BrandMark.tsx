import type { HTMLAttributes } from "react";

import { HermesCoreIcon, RadarCircuitIcon } from "@/components/icons/HermesIcons";

type BrandMarkProps = HTMLAttributes<HTMLDivElement> & {
  compact?: boolean;
  subtitle?: string;
  title?: string;
};

export function BrandMark({
  className,
  compact = false,
  subtitle = "Guardião local da infraestrutura",
  title = "HermesOps Sentinel",
  ...props
}: BrandMarkProps) {
  return (
    <div className={["brand-mark-block", compact ? "compact" : "", className].filter(Boolean).join(" ")} {...props}>
      <div className="brand-mark-badge" aria-hidden="true">
        <HermesCoreIcon className="brand-mark-logo" size={42} />
        <span className="brand-mark-ring" />
      </div>
      <div className="brand-mark-copy">
        <div className="brand-mark-title-row">
          <strong>{title}</strong>
          {!compact ? <span className="brand-mark-kicker">Sentinel</span> : null}
        </div>
        {!compact ? <p>{subtitle}</p> : null}
      </div>
      {!compact ? (
        <div className="brand-mark-chip" aria-hidden="true">
          <RadarCircuitIcon size={14} />
          <span>Centro de comando local</span>
          <HermesCoreIcon size={14} />
        </div>
      ) : null}
    </div>
  );
}
