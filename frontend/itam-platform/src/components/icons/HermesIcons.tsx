import { createElement } from "react";
import type { ReactElement, ReactNode, SVGProps } from "react";

import agentOrbitSvg from "@/assets/icons/hermesops/svg/agent-orbit.svg?raw";
import auditReportSvg from "@/assets/icons/hermesops/svg/audit-report.svg?raw";
import bookCircuitSvg from "@/assets/icons/hermesops/svg/book-circuit.svg?raw";
import conflictSplitSvg from "@/assets/icons/hermesops/svg/conflict-split.svg?raw";
import databasePulseSvg from "@/assets/icons/hermesops/svg/database-pulse.svg?raw";
import documentBoltSvg from "@/assets/icons/hermesops/svg/document-bolt.svg?raw";
import eyeTraceSvg from "@/assets/icons/hermesops/svg/eye-trace.svg?raw";
import hermesCoreSvg from "@/assets/icons/hermesops/svg/hermes-core.svg?raw";
import neuralNodeSvg from "@/assets/icons/hermesops/svg/neural-node.svg?raw";
import packageChipSvg from "@/assets/icons/hermesops/svg/package-chip.svg?raw";
import radarCircuitSvg from "@/assets/icons/hermesops/svg/radar-circuit.svg?raw";
import settingsCircuitSvg from "@/assets/icons/hermesops/svg/settings-circuit.svg?raw";
import shieldCheckSvg from "@/assets/icons/hermesops/svg/shield-check.svg?raw";
import transferCircuitSvg from "@/assets/icons/hermesops/svg/transfer-circuit.svg?raw";

export type HermesIconProps = Omit<SVGProps<SVGSVGElement>, "children"> & {
  size?: number;
  title?: string;
};

export type HermesIconName =
  | "agent-orbit"
  | "audit-report"
  | "book-circuit"
  | "conflict-split"
  | "database-pulse"
  | "document-bolt"
  | "eye-trace"
  | "hermes-core"
  | "neural-node"
  | "package-chip"
  | "radar-circuit"
  | "settings-circuit"
  | "shield-check"
  | "transfer-circuit";

const ALLOWED_SVG_TAGS = new Set(["circle", "defs", "ellipse", "g", "line", "path", "polygon", "polyline", "rect"]);
const SVG_ATTR_MAP: Record<string, string> = {
  "clip-path": "clipPath",
  "clip-rule": "clipRule",
  class: "className",
  "fill-rule": "fillRule",
  "fill-opacity": "fillOpacity",
  "font-family": "fontFamily",
  "font-size": "fontSize",
  "gradient-transform": "gradientTransform",
  "gradient-units": "gradientUnits",
  "marker-end": "markerEnd",
  "marker-mid": "markerMid",
  "marker-start": "markerStart",
  "stroke-dasharray": "strokeDasharray",
  "stroke-dashoffset": "strokeDashoffset",
  "stroke-linecap": "strokeLinecap",
  "stroke-linejoin": "strokeLinejoin",
  "stroke-miterlimit": "strokeMiterlimit",
  "stroke-opacity": "strokeOpacity",
  "stroke-width": "strokeWidth",
  "stop-color": "stopColor",
  "stop-opacity": "stopOpacity",
  "text-anchor": "textAnchor",
  "vector-effect": "vectorEffect",
  "xml:space": "xmlSpace"
};

function mapSvgAttribute(name: string): string | null {
  if (name.startsWith("on")) {
    return null;
  }
  if (name.startsWith("data-") || name.startsWith("aria-")) {
    return name;
  }
  return SVG_ATTR_MAP[name] ?? name;
}

function renderSvgNode(node: Element, key: string): ReactNode {
  const tagName = node.tagName.toLowerCase();
  if (!ALLOWED_SVG_TAGS.has(tagName)) {
    return Array.from(node.children).map((child, index) => renderSvgNode(child, `${key}-${index}`));
  }

  const props: Record<string, string> = {};
  for (const attr of Array.from(node.attributes)) {
    const propName = mapSvgAttribute(attr.name);
    if (!propName) {
      continue;
    }
    props[propName] = attr.value;
  }

  const children = Array.from(node.children).map((child, index) => renderSvgNode(child, `${key}-${index}`));
  return createElement(tagName, { key, ...props }, children.length > 0 ? children : undefined);
}

function parseSvgDocument(svg: string): Element | null {
  if (typeof DOMParser === "undefined") {
    return null;
  }

  const document = new DOMParser().parseFromString(svg, "image/svg+xml");
  const root = document.documentElement;
  if (!root || root.tagName.toLowerCase() !== "svg") {
    return null;
  }

  return root as Element;
}

function parseSvgChildren(svg: string): ReactNode[] {
  const root = parseSvgDocument(svg);
  if (!root) {
    return [];
  }

  return Array.from(root.children).map((child, index) => renderSvgNode(child, `svg-${index}`));
}

function createIcon(svg: string) {
  return function HermesIconComponent({ className, size = 24, title, ...props }: HermesIconProps) {
    const svgDocument = parseSvgDocument(svg);
    const viewBox = svgDocument?.getAttribute("viewBox") ?? "0 0 24 24";

    return (
      <svg
        aria-hidden={title ? undefined : "true"}
        aria-label={title}
        className={className}
        fill="none"
        height={size}
        role={title ? "img" : undefined}
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        viewBox={viewBox}
        width={size}
        xmlns="http://www.w3.org/2000/svg"
        {...props}
      >
        {parseSvgChildren(svg)}
      </svg>
    );
  };
}

export const AgentOrbitIcon = createIcon(agentOrbitSvg);
export const AuditReportIcon = createIcon(auditReportSvg);
export const BookCircuitIcon = createIcon(bookCircuitSvg);
export const ConflictSplitIcon = createIcon(conflictSplitSvg);
export const DatabasePulseIcon = createIcon(databasePulseSvg);
export const DocumentBoltIcon = createIcon(documentBoltSvg);
export const EyeTraceIcon = createIcon(eyeTraceSvg);
export const HermesCoreIcon = createIcon(hermesCoreSvg);
export const NeuralNodeIcon = createIcon(neuralNodeSvg);
export const PackageChipIcon = createIcon(packageChipSvg);
export const RadarCircuitIcon = createIcon(radarCircuitSvg);
export const SettingsCircuitIcon = createIcon(settingsCircuitSvg);
export const ShieldCheckIcon = createIcon(shieldCheckSvg);
export const TransferCircuitIcon = createIcon(transferCircuitSvg);

const iconMap: Record<HermesIconName, (props: HermesIconProps) => ReactElement> = {
  "agent-orbit": AgentOrbitIcon,
  "audit-report": AuditReportIcon,
  "book-circuit": BookCircuitIcon,
  "conflict-split": ConflictSplitIcon,
  "database-pulse": DatabasePulseIcon,
  "document-bolt": DocumentBoltIcon,
  "eye-trace": EyeTraceIcon,
  "hermes-core": HermesCoreIcon,
  "neural-node": NeuralNodeIcon,
  "package-chip": PackageChipIcon,
  "radar-circuit": RadarCircuitIcon,
  "settings-circuit": SettingsCircuitIcon,
  "shield-check": ShieldCheckIcon,
  "transfer-circuit": TransferCircuitIcon
};

export function HermesIcon({ name, ...props }: HermesIconProps & { name: HermesIconName }) {
  const Icon = iconMap[name];
  return <Icon {...props} />;
}
