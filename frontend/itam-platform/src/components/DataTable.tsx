import type { ReactNode } from "react";

import { EmptyState } from "@/components/StateBlocks";

type Column<T> = {
  key: keyof T | string;
  label: string;
  render?: (item: T) => ReactNode;
  sortable?: boolean;
  className?: string;
};

export function DataTable<T extends { id: string }>({
  columns,
  items,
  emptyMessage = "Nenhum registro encontrado.",
  emptyTitle,
  emptyDescription,
  emptyActions,
  sortBy,
  sortOrder,
  onSort,
  rowActions
}: {
  columns: Column<T>[];
  items: T[];
  emptyMessage?: string;
  emptyTitle?: ReactNode;
  emptyDescription?: ReactNode;
  emptyActions?: ReactNode;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (key: string) => void;
  rowActions?: (item: T) => ReactNode;
}) {
  const colSpan = columns.length + (rowActions ? 1 : 0);
  const isEmpty = items.length === 0;

  return (
    <div className={isEmpty ? "table-wrap table-wrap-empty" : "table-wrap"} role="region" aria-label="Tabela operacional" tabIndex={0}>
      <table className="data-table">
        <caption className="sr-only">Tabela operacional</caption>
        <thead>
          <tr>
            {columns.map((column) => {
              const key = String(column.key);
              const active = sortBy === key;
              return (
                <th key={key} scope="col">
                  {column.sortable && onSort ? (
                    <button className="sort-button" type="button" onClick={() => onSort(key)} aria-sort={active ? (sortOrder === "asc" ? "ascending" : "descending") : undefined}>
                      <span>{column.label}</span>
                      {active ? <span aria-hidden>{sortOrder === "asc" ? "↑" : "↓"}</span> : null}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              );
            })}
            {rowActions ? <th scope="col" className="table-actions-heading">Ações</th> : null}
          </tr>
        </thead>
        <tbody>
          {isEmpty ? (
            <tr className="table-empty-row">
              <td colSpan={colSpan}>
                <div className="table-empty-state">
                  <EmptyState
                    title={emptyTitle ?? emptyMessage}
                    description={emptyDescription}
                  >
                    {emptyActions}
                  </EmptyState>
                </div>
              </td>
            </tr>
          ) : null}
          {items.map((item) => (
            <tr key={item.id}>
              {columns.map((column) => (
                <td className={column.className} key={String(column.key)}>
                  {column.render ? column.render(item) : String(item[column.key as keyof T] ?? "-")}
                </td>
              ))}
              {rowActions ? <td className="row-actions">{rowActions(item)}</td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
