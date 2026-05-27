"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { AuthGate } from "@/components/AuthGate";
import { EmptyState } from "@/components/EmptyState";
import { Pagination } from "@/components/Pagination";
import { api } from "@/lib/api";
import type { PageResponse, Task } from "@/lib/types";

export default function TasksPage() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PageResponse<Task> | null>(null);

  useEffect(() => {
    api<PageResponse<Task>>(`/tasks?page=${page}&page_size=20`)
      .then(setData)
      .catch(() => {
        setData({ items: [], total: 0, page, page_size: 20 });
      });
  }, [page]);

  return (
    <AuthGate>
      <AppShell title="任务中心">
        {!data || data.items.length === 0 ? (
          <EmptyState title="暂无任务" description="这里适合接入导入、生成、同步等异步任务。" />
        ) : (
          <div className="space-y-3">
            {data.items.map((task) => (
              <article key={task.id} className="rounded-lg border border-border bg-card p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="font-semibold">{task.name}</h2>
                    <p className="mt-1 text-sm text-muted-foreground">{task.message}</p>
                  </div>
                  <span className="rounded-md bg-muted px-2 py-1 text-xs">{task.status}</span>
                </div>
              </article>
            ))}
          </div>
        )}
        {data ? (
          <Pagination page={page} total={data.total} pageSize={data.page_size} onPage={setPage} />
        ) : null}
      </AppShell>
    </AuthGate>
  );
}
