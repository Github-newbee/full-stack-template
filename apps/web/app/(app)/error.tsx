"use client";

import { RefreshCw } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";

export default function AppError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <EmptyState title="页面加载失败" description="请稍后重试或检查 API 服务状态。" />
      <div className="mt-4 flex justify-center">
        <Button type="button" variant="outline" onClick={reset}>
          <RefreshCw />
          重新加载
        </Button>
      </div>
    </div>
  );
}
