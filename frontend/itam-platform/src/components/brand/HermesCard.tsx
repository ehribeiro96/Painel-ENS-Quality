import type { HTMLAttributes, ReactNode } from "react";

type HermesCardVariant = "default" | "active" | "success" | "warning" | "danger" | "info";

export function HermesCard({
  children,
  className,
  description,
  icon,
  title,
  variant = "default",
  eyebrow,
  ...props
}: Omit<HTMLAttributes<HTMLElement>, "title"> & {
  description?: ReactNode;
  icon?: ReactNode;
  title?: ReactNode;
  eyebrow?: ReactNode;
  variant?: HermesCardVariant;
}) {
  return (
    <article className={["hermes-card", `variant-${variant}`, className].filter(Boolean).join(" ")} {...props}>
      {(eyebrow || title || icon || description) ? (
        <header className="hermes-card-header">
          <div className="hermes-card-copy">
            {eyebrow ? <div className="hermes-card-eyebrow">{eyebrow}</div> : null}
            {title ? <div className="hermes-card-title">{title}</div> : null}
            {description ? <div className="hermes-card-description">{description}</div> : null}
          </div>
          {icon ? <div className="hermes-card-icon" aria-hidden="true">{icon}</div> : null}
        </header>
      ) : null}
      {children}
    </article>
  );
}
