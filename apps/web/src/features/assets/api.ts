import { api } from "@/lib/api";
import type { Asset, PageResponse } from "@/lib/types";

export async function listAssets(options: { signal?: AbortSignal } = {}) {
  return api<PageResponse<Asset>>("/assets", {
    signal: options.signal,
  });
}
