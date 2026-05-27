"use client";

import { Loader2, LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123456");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success("登录成功");
      router.push("/dashboard");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm rounded-lg border border-border bg-card p-6 shadow-sm"
      >
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">管理台登录</h1>
          <p className="mt-2 text-sm text-muted-foreground">使用默认管理员账号进入模板后台。</p>
        </div>
        <label className="mb-4 block text-sm font-medium">
          邮箱
          <Input
            className="mt-2"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            autoComplete="email"
          />
        </label>
        <label className="mb-6 block text-sm font-medium">
          密码
          <Input
            className="mt-2"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            autoComplete="current-password"
          />
        </label>
        <Button className="w-full" type="submit" disabled={loading}>
          {loading ? <Loader2 className="size-4 animate-spin" /> : <LogIn className="size-4" />}
          登录
        </Button>
      </form>
    </main>
  );
}
