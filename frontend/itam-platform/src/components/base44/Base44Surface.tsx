import type { ElementType, ReactNode } from "react";
import { createElement } from "react";

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
  return createElement(Component, { ...props, className: `base44-surface ${className}`.trim() }, children);
}
