import { api } from "@/lib/api";
import type { PageResponse, Task } from "@/lib/types";

export async function listTasks({
  page,
  pageSize,
  signal,
}: {
  page: number;
  pageSize: number;
  signal?: AbortSignal;
}) {
  return api<PageResponse<Task>>(`/tasks?page=${page}&page_size=${pageSize}`, { signal });
}
