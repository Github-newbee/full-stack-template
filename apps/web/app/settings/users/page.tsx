"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { AuthGate } from "@/components/AuthGate";
import { EmptyState } from "@/components/EmptyState";
import { Pagination } from "@/components/Pagination";
import { api } from "@/lib/api";
import type { PageResponse, User } from "@/lib/types";

export default function UsersPage() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PageResponse<User> | null>(null);

  useEffect(() => {
    api<PageResponse<User>>(`/users?page=${page}&page_size=20`)
      .then(setData)
      .catch(() => {
        setData({ items: [], total: 0, page, page_size: 20 });
      });
  }, [page]);

  return (
    <AuthGate>
      <AppShell title="用户管理">
        {!data || data.items.length === 0 ? (
          <EmptyState title="暂无用户" description="创建用户接口已就绪，可按业务需要接入表单。" />
        ) : (
          <div className="overflow-hidden rounded-lg border border-border bg-card">
            <table className="w-full text-left text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">邮箱</th>
                  <th className="px-4 py-3 font-medium">姓名</th>
                  <th className="px-4 py-3 font-medium">状态</th>
                  <th className="px-4 py-3 font-medium">角色</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((user) => (
                  <tr key={user.id} className="border-t border-border">
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3">{user.full_name}</td>
                    <td className="px-4 py-3">{user.is_active ? "启用" : "禁用"}</td>
                    <td className="px-4 py-3">{user.roles.map((role) => role.name).join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {data ? (
          <Pagination page={page} total={data.total} pageSize={data.page_size} onPage={setPage} />
        ) : null}
      </AppShell>
    </AuthGate>
  );
}
