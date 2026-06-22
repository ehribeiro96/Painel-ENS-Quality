import type { ApoemaAsset } from "../types";
import { StatusPill } from "./StatusPill";

const statusToneMap = {
  healthy: "success",
  review: "warning",
  maintenance: "info",
  offline: "neutral"
} as const;

export function DataTable({
  rows,
  selectedId,
  onSelect
}: {
  rows: ApoemaAsset[];
  selectedId: string;
  onSelect: (asset: ApoemaAsset) => void;
}) {
  return (
    <div className="apoema-table-wrap">
      <table className="apoema-table">
        <thead>
          <tr>
            <th>Ativo</th>
            <th>Categoria</th>
            <th>Responsável</th>
            <th>Local</th>
            <th>Status</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const tone = statusToneMap[row.status];
            return (
              <tr
                key={row.id}
                className={row.id === selectedId ? "is-selected" : ""}
                onClick={() => onSelect(row)}
              >
                <td>
                  <strong>{row.name}</strong>
                  <span>{row.id}</span>
                </td>
                <td>{row.category}</td>
                <td>{row.owner}</td>
                <td>{row.location}</td>
                <td>
                  <StatusPill tone={tone}>{row.status}</StatusPill>
                </td>
                <td>
                  <div className="apoema-score">
                    <span>{row.score}%</span>
                    <div className="apoema-score-bar">
                      <i style={{ width: `${row.score}%` }} />
                    </div>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
