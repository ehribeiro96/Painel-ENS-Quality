import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type StatCard = {
  label: ReactNode;
  value: ReactNode;
  detail?: ReactNode;
};

export function DonorPanelPageLayout({
  eyebrow,
  title,
  description,
  actions,
  stats,
  children,
  className,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  stats?: StatCard[];
  children?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("space-y-6 overflow-x-hidden pb-4", className)}>
      <section className="overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_20px_60px_-26px_rgba(0,0,0,0.75)] md:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            {eyebrow ? <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">{eyebrow}</p> : null}
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50 md:text-3xl">{title}</h2>
            {description ? <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 md:text-base">{description}</p> : null}
          </div>
          {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
        </div>

        {stats && stats.length > 0 ? (
          <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {stats.map((item, index) => (
              <article
                key={`${String(item.label)}-${index}`}
                className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4 shadow-[0_12px_30px_-24px_rgba(0,0,0,0.75)]"
              >
                <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{item.label}</p>
                <p className="mt-2 text-2xl font-semibold text-slate-50">{item.value}</p>
                {item.detail ? <p className="mt-2 text-sm leading-6 text-slate-400">{item.detail}</p> : null}
              </article>
            ))}
          </div>
        ) : null}
      </section>

      {children}
    </div>
  );
}
