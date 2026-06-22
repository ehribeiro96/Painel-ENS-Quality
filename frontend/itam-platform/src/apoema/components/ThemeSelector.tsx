import type { ThemeMode } from "../types";

export function ThemeSelector({
  value,
  onChange
}: {
  value: ThemeMode;
  onChange: (value: ThemeMode) => void;
}) {
  return (
    <div className="apoema-theme-selector" role="group" aria-label="Selecionar tema">
      {[
        { id: "light", label: "Claro" },
        { id: "dark", label: "Escuro" },
        { id: "auto", label: "Automático" }
      ].map((option) => (
        <button
          key={option.id}
          type="button"
          className={`apoema-theme-button ${value === option.id ? "is-active" : ""}`}
          onClick={() => onChange(option.id as ThemeMode)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
