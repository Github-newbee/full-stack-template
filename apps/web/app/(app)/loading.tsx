import { Loader2 } from "lucide-react";

export default function AppLoading() {
  return (
    <div className="grid min-h-64 place-items-center rounded-lg border border-border bg-card">
      <Loader2 className="size-6 animate-spin text-primary" aria-label="加载中" />
    </div>
  );
}
