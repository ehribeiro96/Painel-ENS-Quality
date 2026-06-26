# Designer Template Contract

## Source of truth
Templates are server-owned and resolved only from `templates_library/{canal}/{kv}/`. The external project uses `execution/select_template.py` to pick the first available image and exposes `/templates` and `/banners/form-options` from that catalog.

## Allowed high-level options
- `modo_geracao`: `peca_unica`, `enxoval`
- `canal`: `01_feed_instagram; 02_story_instagram; 03_banner_interno_desktop; 04_banner_interno_mobile; 05_AIDA_whatsapp; 05_whatsapp; 08_topo_email`
- `kv`: `graduacao; imersoes; institucional; pos; qualificacoes; tudo-sobre-seguros`
- `box2`: optional and may be empty
- `persona_image`: optional `.png`, `.jpg`, `.jpeg` upload

## Template rules
- templates are allowlisted by backend catalog
- templates must include `template_context.json` for contract review
- planner payloads are server-owned and should not be hardcoded in the frontend
- prompt changes must preserve template geometry and brand-safe elements

## Safety terms
TEMPLATE_ALLOWLIST, FORM_OPTION_ALLOWLIST, PROMPT_INPUT_VALIDATION.

## Notes
Some external template directories use planner payloads and some do not; the contract should surface only the canonical allowlist and keep review metadata backend-side.
