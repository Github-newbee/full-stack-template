"use client";

import { Boxes, LayoutDashboard, ListChecks, LogOut, Shield, Users } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "概览", icon: LayoutDashboard },
  { href: "/settings/users", label: "用户", icon: Users },
  { href: "/settings/roles", label: "角色", icon: Shield },
  { href: "/tasks", label: "任务", icon: ListChecks },
  { href: "/assets", label: "文件", icon: Boxes },
];

export function AppShell({
  title,
  action,
  children,
}: {
  title: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  function onLogout() {
    logout();
    router.push("/login");
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="border-r border-border bg-card px-3 py-4">
        <div className="px-3 pb-5">
          <div className="text-base font-semibold">Admin Template</div>
          <div className="mt-1 text-xs text-muted-foreground">{user?.email}</div>
        </div>
        <nav className="flex gap-1 overflow-x-auto lg:block lg:space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex min-w-max items-center gap-2 rounded-md px-3 py-2 text-sm transition",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <item.icon className="size-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="min-w-0">
        <header className="flex items-center justify-between gap-4 border-b border-border bg-card px-5 py-4">
          <h1 className="text-xl font-semibold">{title}</h1>
          <div className="flex items-center gap-2">
            {action}
            <Button variant="secondary" type="button" onClick={onLogout} aria-label="退出登录">
              <LogOut className="size-4" />
            </Button>
          </div>
        </header>
        <div className="p-5">{children}</div>
      </main>
    </div>
  );
}
