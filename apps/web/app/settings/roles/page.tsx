"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { AuthGate } from "@/components/AuthGate";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/lib/api";
import type { Role } from "@/lib/types";

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);

  useEffect(() => {
    api<Role[]>("/roles")
      .then(setRoles)
      .catch(() => setRoles([]));
  }, []);

  return (
    <AuthGate>
      <AppShell title="角色权限">
        {roles.length === 0 ? (
          <EmptyState title="暂无角色" description="默认角色会在 API 启动时初始化。" />
        ) : (
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
        )}
      </AppShell>
    </AuthGate>
  );
}
