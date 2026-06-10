"use client";

import { Loader2 } from "lucide-react";
import { useCallback } from "react";
import { EmptyState } from "@/components/EmptyState";
import { useAsync } from "@/hooks/useAsync";
import type { Asset } from "@/lib/types";
import { listAssets } from "../api";

export function AssetsTable() {
  const loadAssets = useCallback((signal: AbortSignal) => listAssets({ signal }), []);
  const { data, loading, error } = useAsync(loadAssets);
  const assets: Asset[] = data?.items ?? [];

  if (loading && !data) {
    return (
      <div className="grid min-h-64 place-items-center rounded-lg border border-border bg-card">
        <Loader2 className="size-6 animate-spin text-primary" aria-label="加载文件数据" />
      </div>
    );
  }

  if (error) {
    return <EmptyState title="文件数据加载失败" description="请稍后重试或检查 API 服务状态。" />;
  }

  if (assets.length === 0) {
    return (
      <EmptyState
        title="暂无文件"
        description="上传接口已就绪，可扩展为图片、文档或模型文件管理。"
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <table className="w-full text-left text-sm">
        <thead className="bg-muted text-muted-foreground">
          <tr>
            <th className="px-4 py-3 font-medium">文件名</th>
            <th className="px-4 py-3 font-medium">类型</th>
            <th className="px-4 py-3 font-medium">大小</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((asset) => (
            <tr key={asset.id} className="border-t border-border">
              <td className="px-4 py-3">{asset.filename}</td>
              <td className="px-4 py-3">{asset.content_type}</td>
              <td className="px-4 py-3">{asset.size} bytes</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
