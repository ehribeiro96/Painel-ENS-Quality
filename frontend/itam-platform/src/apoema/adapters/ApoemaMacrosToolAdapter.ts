import { api } from "@/lib/api";
import type { MacroGeneration, MacroRenderResponse, MacroTemplate } from "@/lib/types";

export const ApoemaMacrosToolAdapter = {
  listTemplates(token: string, params = ""): Promise<MacroTemplate[]> {
    return api.macroTemplates(token, params);
  },

  renderMacro(token: string, payload: Record<string, unknown>): Promise<MacroRenderResponse> {
    return api.macroRender(token, payload);
  },

  generateMacro(token: string, payload: Record<string, unknown>): Promise<MacroGeneration> {
    return api.macroGenerate(token, payload);
  },

  markMacroCopied(token: string, generationId: string): Promise<MacroGeneration> {
    return api.macroMarkCopied(token, generationId);
  },
};
