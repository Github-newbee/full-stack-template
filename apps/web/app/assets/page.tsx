"use client";

import { Upload } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { AuthGate } from "@/components/AuthGate";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Asset, PageResponse } from "@/lib/types";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);

  useEffect(() => {
    api<PageResponse<Asset>>("/assets")
      .then((data) => setAssets(data.items))
      .catch(() => setAssets([]));
  }, []);

  return (
    <AuthGate>
      <AppShell
        title="文件资产"
        action={
          <Button type="button">
            <Upload className="size-4" />
            上传
          </Button>
        }
      >
        {assets.length === 0 ? (
          <EmptyState
            title="暂无文件"
            description="上传接口已就绪，可扩展为图片、文档或模型文件管理。"
          />
        ) : (
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
        )}
      </AppShell>
    </AuthGate>
  );
}
