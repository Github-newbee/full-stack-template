import type { User } from "@/lib/types";

export function getPermissionCodes(user: User | null) {
  return new Set(user?.roles.flatMap((role) => role.permissions.map((item) => item.code)));
}

export function canWriteUsers(user: User | null, permissions: Set<string>) {
  return Boolean(user?.is_superuser || permissions.has("users.write"));
}

export function canReadRoles(user: User | null, permissions: Set<string>) {
  return Boolean(user?.is_superuser || permissions.has("roles.read"));
}
