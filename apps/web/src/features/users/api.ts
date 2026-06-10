import { api } from "@/lib/api";
import type { PageResponse, User } from "@/lib/types";
import type { UserFormValues } from "./components/UserFormDialog";

export type UserPayload = {
  username: string;
  email: string | null;
  full_name: string;
  is_active: boolean;
  password?: string;
  role_ids?: string[];
  is_superuser?: boolean;
};

export function buildUserPayload({
  values,
  canManageRoles,
  canManageSuperusers,
  includeEmptyRoles,
}: {
  values: UserFormValues;
  canManageRoles: boolean;
  canManageSuperusers: boolean;
  includeEmptyRoles: boolean;
}): UserPayload {
  const payload: UserPayload = {
    username: values.username,
    email: values.email || null,
    full_name: values.full_name,
    is_active: values.is_active,
  };

  if (values.password) {
    payload.password = values.password;
  }
  if (canManageRoles) {
    payload.role_ids = values.role_ids;
  } else if (includeEmptyRoles) {
    payload.role_ids = [];
  }
  if (canManageSuperusers) {
    payload.is_superuser = values.is_superuser;
  }

  return payload;
}

export async function listUsers({
  page,
  pageSize,
  signal,
}: {
  page: number;
  pageSize: number;
  signal?: AbortSignal;
}) {
  return api<PageResponse<User>>(`/users?page=${page}&page_size=${pageSize}`, { signal });
}

export async function createUser(payload: UserPayload) {
  return api<User>("/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateUser(userId: string, payload: UserPayload) {
  return api<User>(`/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteUser(userId: string) {
  return api<void>(`/users/${userId}`, { method: "DELETE" });
}
