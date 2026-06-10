"use client";

import { Loader2 } from "lucide-react";
import { useCallback, useState } from "react";
import { EmptyState } from "@/components/EmptyState";
import { DataPagination } from "@/components/ui/pagination";
import { useAsync } from "@/hooks/useAsync";
import type { PageResponse, Task } from "@/lib/types";
import { listTasks } from "../api";

const TASK_PAGE_SIZE = 20;

export function TasksList() {
  const [page, setPage] = useState(1);
  const loadTasks = useCallback(
    (signal: AbortSignal) => listTasks({ page, pageSize: TASK_PAGE_SIZE, signal }),
    [page],
  );
  const { data, loading, error } = useAsync<PageResponse<Task>>(loadTasks);

  if (loading && !data) {
    return (
      <div className="grid min-h-64 place-items-center rounded-lg border border-border bg-card">
        <Loader2 className="size-6 animate-spin text-primary" aria-label="加载任务数据" />
      </div>
    );
  }

  if (error) {
    return <EmptyState title="任务数据加载失败" description="请稍后重试或检查 API 服务状态。" />;
  }

  return (
    <>
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
        <DataPagination
          page={page}
          total={data.total}
          pageSize={data.page_size}
          onPageChange={setPage}
        />
      ) : null}
    </>
  );
}
