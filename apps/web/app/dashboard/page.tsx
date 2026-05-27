import { Activity, Database, FileUp, ShieldCheck } from "lucide-react";
import { AuthGate } from "@/components/AuthGate";
import { AppShell } from "@/components/AppShell";

const metrics = [
  { label: "API 状态", value: "Ready", icon: Activity },
  { label: "用户权限", value: "RBAC", icon: ShieldCheck },
  { label: "文件存储", value: "Local volume", icon: FileUp },
  { label: "数据库", value: "SQLAlchemy", icon: Database },
];

export default function DashboardPage() {
  return (
    <AuthGate>
      <AppShell title="概览">
        <section className="grid gap-4 md:grid-cols-4">
          {metrics.map((item) => (
            <div key={item.label} className="rounded-lg border border-border bg-card p-4">
              <div className="mb-3 flex size-9 items-center justify-center rounded-md bg-muted">
                <item.icon className="size-4 text-primary" />
              </div>
              <div className="text-sm text-muted-foreground">{item.label}</div>
              <div className="mt-1 text-xl font-semibold">{item.value}</div>
            </div>
          ))}
        </section>
        <section className="mt-6 rounded-lg border border-border bg-card p-5">
          <h2 className="text-lg font-semibold">模板能力</h2>
          <div className="mt-4 grid gap-3 text-sm text-muted-foreground md:grid-cols-2">
            <p>后端已内置登录、角色权限、任务中心、文件资产和健康检查。</p>
            <p>前端已内置 API client、AuthProvider、AppShell、分页和空状态组件。</p>
          </div>
        </section>
      </AppShell>
    </AuthGate>
  );
}
