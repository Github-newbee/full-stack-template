"use client";

import { Loader2 } from "lucide-react";
import { useCallback } from "react";
import { EmptyState } from "@/components/EmptyState";
import { useAsync } from "@/hooks/useAsync";
import type { Role } from "@/lib/types";
import { listRoles } from "../api";

export function RolesGrid() {
  const loadRoles = useCallback((signal: AbortSignal) => listRoles({ signal }), []);
  const { data, loading, error } = useAsync<Role[]>(loadRoles);
  const roles = data ?? [];

  if (loading && !data) {
    return (
      <div className="grid min-h-64 place-items-center rounded-lg border border-border bg-card">
        <Loader2 className="size-6 animate-spin text-primary" aria-label="加载角色数据" />
      </div>
    );
  }

  if (error) {
    return <EmptyState title="角色数据加载失败" description="请稍后重试或检查 API 服务状态。" />;
  }

  if (roles.length === 0) {
    return <EmptyState title="暂无角色" description="默认角色会在 API 启动时初始化。" />;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {roles.map((role) => (
        <article key={role.id} className="rounded-lg border border-border bg-card p-4">
          <h2 className="font-semibold">{role.name}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{role.description}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {role.permissions.map((permission) => (
              <span key={permission.code} className="rounded-md bg-muted px-2 py-1 text-xs">
                {permission.code}
              </span>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
