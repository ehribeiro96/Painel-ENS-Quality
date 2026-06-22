import type { ReactNode } from "react";
import type { ApoemaCommand } from "../types";
import { ArrowRight, FolderInput, ClipboardList, RefreshCw } from "lucide-react";

const commandIcons: Record<string, ReactNode> = {
  "folder-input": <FolderInput size={18} />,
  "clipboard-list": <ClipboardList size={18} />,
  "refresh-cw": <RefreshCw size={18} />
};

export function CommandCard({ command }: { command: ApoemaCommand }) {
  return (
    <button type="button" className="apoema-command-card">
      <span className="apoema-command-icon">{commandIcons[command.icon] ?? <ArrowRight size={18} />}</span>
      <span className="apoema-command-content">
        <strong>{command.title}</strong>
        <span>{command.description}</span>
      </span>
      <span className="apoema-command-action">
        {command.action}
        <ArrowRight size={14} />
      </span>
    </button>
  );
}
