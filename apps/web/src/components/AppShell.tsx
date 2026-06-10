"use client";

import {
  Boxes,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Shield,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import type { User } from "@/lib/types";
import { cn } from "@/lib/utils";

const SIDEBAR_STORAGE_KEY = "finance-sidebar-collapsed";
let sidebarCollapsedCache = false;

const navItems = [
  { href: "/dashboard", label: "概览", icon: LayoutDashboard },
  { href: "/settings/users", label: "用户", icon: Users },
  { href: "/settings/roles", label: "角色", icon: Shield },
  { href: "/tasks", label: "任务", icon: ListChecks },
  { href: "/assets", label: "文件", icon: Boxes },
];

const routeTitles = [
  { href: "/settings/users", title: "用户管理" },
  { href: "/settings/roles", title: "角色权限" },
  { href: "/dashboard", title: "概览" },
  { href: "/tasks", title: "任务中心" },
  { href: "/assets", title: "文件资产" },
];

function getUserDisplayName(user: User | null) {
  return user?.full_name?.trim() || user?.username || "用户";
}

function getUserInitial(name: string) {
  return name.trim().charAt(0).toUpperCase() || "用";
}

function getRouteTitle(pathname: string) {
  return (
    routeTitles.find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`))
      ?.title ?? "财务系统"
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(sidebarCollapsedCache);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const title = getRouteTitle(pathname);
  const userDisplayName = getUserDisplayName(user);
  const userInitial = getUserInitial(userDisplayName);

  useEffect(() => {
    try {
      const storedCollapsed = window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
      sidebarCollapsedCache = storedCollapsed;
      setSidebarCollapsed(storedCollapsed);
    } catch {
      // Keep the expanded default when browser storage is unavailable.
    }
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileMenuOpen) {
      return;
    }

    const previousOverflow = document.body.style.overflow;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMobileMenuOpen(false);
      }
    }

    function onDesktopChange(event: MediaQueryListEvent) {
      if (event.matches) {
        setMobileMenuOpen(false);
      }
    }

    const desktopMedia = window.matchMedia("(min-width: 64rem)");
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);
    desktopMedia.addEventListener("change", onDesktopChange);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
      desktopMedia.removeEventListener("change", onDesktopChange);
    };
  }, [mobileMenuOpen]);

  function onLogout() {
    logout();
    router.push("/login");
  }

  function onToggleSidebar() {
    const nextCollapsed = !sidebarCollapsed;
    sidebarCollapsedCache = nextCollapsed;
    setSidebarCollapsed(nextCollapsed);

    try {
      window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(nextCollapsed));
    } catch {
      // The current session can still use the toggle without persistence.
    }
  }

  return (
    <div
      className={cn(
        "min-h-screen lg:grid",
        sidebarCollapsed
          ? "lg:grid-cols-[72px_minmax(0,1fr)]"
          : "lg:grid-cols-[240px_minmax(0,1fr)]",
      )}
    >
      {mobileMenuOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-950/35 backdrop-blur-[1px] lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-label="关闭导航菜单"
        />
      ) : null}
      <aside
        id="app-sidebar"
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col border-r border-border bg-card px-3 py-3 shadow-xl transition-transform duration-200 ease-out",
          "lg:static lg:z-auto lg:w-auto lg:max-w-none lg:translate-x-0 lg:shadow-none",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between gap-3 px-2 pb-4">
          <div className={cn("text-xl font-semibold", sidebarCollapsed && "lg:hidden")}>
            财务系统
          </div>
          <Button
            variant="ghost"
            type="button"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="关闭导航菜单"
            className="size-9 shrink-0 px-0 lg:hidden"
          >
            <X className="size-5" />
          </Button>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                aria-label={sidebarCollapsed ? item.label : undefined}
                title={sidebarCollapsed ? item.label : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  sidebarCollapsed && "lg:justify-center lg:gap-0 lg:px-0",
                )}
              >
                <item.icon className="size-4 shrink-0" />
                <span className={cn(sidebarCollapsed && "lg:hidden")}>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="min-w-0">
        <header className="flex h-14 items-center justify-between gap-4 border-b border-border bg-card px-4">
          <div className="flex min-w-0 items-center gap-2">
            <Button
              variant="ghost"
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="打开导航菜单"
              aria-controls="app-sidebar"
              aria-expanded={mobileMenuOpen}
              className="size-9 shrink-0 px-0 lg:hidden"
            >
              <Menu className="size-5" />
            </Button>
            <Button
              variant="ghost"
              type="button"
              onClick={onToggleSidebar}
              aria-label={sidebarCollapsed ? "展开侧边栏" : "折叠侧边栏"}
              aria-controls="app-sidebar"
              aria-expanded={!sidebarCollapsed}
              title={sidebarCollapsed ? "展开侧边栏" : "折叠侧边栏"}
              className="hidden size-8 shrink-0 px-0 lg:inline-flex"
            >
              {sidebarCollapsed ? (
                <PanelLeftOpen className="size-4" />
              ) : (
                <PanelLeftClose className="size-4" />
              )}
            </Button>
            <h1 className="truncate text-lg font-semibold">{title}</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex min-w-0 items-center gap-2">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                {userInitial}
              </div>
              <div className="hidden min-w-0 leading-tight sm:block">
                <div className="truncate text-sm font-medium">{userDisplayName}</div>
                <div className="truncate text-xs text-muted-foreground">{user?.username}</div>
              </div>
            </div>
            <Button
              variant="secondary"
              type="button"
              onClick={onLogout}
              aria-label="退出登录"
              className="size-8 shrink-0 rounded-full px-0"
            >
              <LogOut className="size-4" />
            </Button>
          </div>
        </header>
        <div className="p-4 sm:p-5">{children}</div>
      </main>
    </div>
  );
}
