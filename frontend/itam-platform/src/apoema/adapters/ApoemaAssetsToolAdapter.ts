import { api } from "@/lib/api";
import type { Asset } from "@/lib/types";

export const ApoemaAssetsToolAdapter = {
  listAssets(token: string, params = "") {
    return api.assets(token, params);
  },

  getAsset(token: string, assetId: string): Promise<Asset> {
    return api.asset(token, assetId);
  },
};
