import { api } from "@/lib/api";
import type { Role } from "@/lib/types";

export async function listRoles(options: { signal?: AbortSignal } = {}) {
  return api<Role[]>("/roles", {
    signal: options.signal,
  });
}
