import { useMemo } from "react";
import { useThemeMode } from "../hooks/useThemeMode";
import { ThemeSelector } from "../components/ThemeSelector";
import { apoemaPreferences } from "../data";
import { StatusPill } from "../components/StatusPill";
import { CheckCircle2, LayoutGrid, Shield, Sparkles } from "lucide-react";

export function SettingsPage() {
  const theme = useThemeMode();
  const preferenceList = useMemo(() => apoemaPreferences, []);

  return (
    <div className="apoema-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="info">Ajustes de experiência</StatusPill>
          <h1>Tema, segurança e densidade operacional.</h1>
          <p>Configure a aparência do console e as salvaguardas de fluxo assistido.</p>
        </div>
        <ThemeSelector value={theme.mode} onChange={theme.setMode} />
      </section>

      <section className="apoema-settings-grid">
        <article className="apoema-panel">
          <div className="apoema-section-head">
            <h2>Preferências</h2>
            <span>UI profile</span>
          </div>
          <div className="apoema-preference-list">
            {preferenceList.map((pref) => (
              <div key={pref.label} className="apoema-preference-item">
                <div className="apoema-preference-icon">
                  {pref.enabled ? <CheckCircle2 size={16} /> : <LayoutGrid size={16} />}
                </div>
                <div>
                  <strong>{pref.label}</strong>
                  <p>{pref.description}</p>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="apoema-panel">
          <div className="apoema-section-head">
            <h2>Segurança</h2>
            <span>Operational guard rails</span>
          </div>
          <div className="apoema-settings-notes">
            <div className="apoema-settings-note">
              <Shield size={16} />
              <div>
                <strong>Proteção de contexto</strong>
                <p>Arquivos sensíveis e credenciais são destacados antes de qualquer ação.</p>
              </div>
            </div>
            <div className="apoema-settings-note">
              <Sparkles size={16} />
              <div>
                <strong>Assistência centrada em IA</strong>
                <p>O fluxo prioriza resumo, recomendação e execução mockada segura.</p>
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
