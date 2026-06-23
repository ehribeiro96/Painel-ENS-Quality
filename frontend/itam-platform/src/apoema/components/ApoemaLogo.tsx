export function ApoemaLogo({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`apoema-logo ${compact ? "is-compact" : ""}`} aria-label="Apoema">
      <svg viewBox="0 0 128 128" className="apoema-logo-mark" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="apoema-mark-stroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--apoema-teal)" />
            <stop offset="50%" stopColor="var(--apoema-cyan)" />
            <stop offset="100%" stopColor="var(--apoema-copper)" />
          </linearGradient>
        </defs>
        <g fill="none" stroke="url(#apoema-mark-stroke)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
          <path d="M64 7v28" />
          <path d="M64 93v28" />
          <path d="M21 35v16" />
          <path d="M107 35v16" />
          <path d="M21 77v16" />
          <path d="M107 77v16" />
          <path d="M34 21l-13 13" />
          <path d="M94 21l13 13" />
          <path d="M34 107l-13-13" />
          <path d="M94 107l13-13" />
          <path d="M64 20l30 30-30 30-30-30z" />
          <path d="M64 44l16 16-16 16-16-16z" />
          <path d="M64 76l20 20-20 20-20-20z" />
        </g>
        <circle cx="64" cy="64" r="4.5" fill="var(--apoema-cyan)" />
      </svg>
      <div className="apoema-logo-text">
        <strong>Apoema</strong>
        {!compact && <span>Console Inteligente de Operações, Inventário e Suporte N2</span>}
      </div>
    </div>
  );
}
