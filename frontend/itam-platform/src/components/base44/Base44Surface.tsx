import type { ElementType, ReactNode } from "react";
import { createElement } from "react";
import { cn } from "@/lib/utils";

export function Base44Surface({
  children,
  className = "",
  as,
  ...props
}: {
  children: ReactNode;
  className?: string;
  as?: ElementType;
  [key: string]: unknown;
}) {
  const Component = as ?? "section";
  return createElement(
    Component,
    {
      ...props,
      className: cn(
        "rounded-[26px] border border-white/10 bg-white/[0.04] p-4 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)] backdrop-blur-xl md:p-5",
        className,
      ),
    },
    children,
  );
}
