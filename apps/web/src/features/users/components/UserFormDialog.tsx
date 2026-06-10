"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, X } from "lucide-react";
import { useEffect, useMemo } from "react";
import { type UseFormRegisterReturn, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getErrorMessage } from "@/lib/api";
import type { Role, User } from "@/lib/types";

const optionalEmailSchema = z
  .string()
  .trim()
  .refine((value) => value === "" || z.string().email().safeParse(value).success, {
    message: "请输入有效的邮箱",
  });

const userFormSchema = z.object({
  username: z.string().trim().min(1, "请输入用户名").max(80, "用户名不能超过 80 个字符"),
  email: optionalEmailSchema,
  full_name: z.string().trim().max(120, "姓名不能超过 120 个字符"),
  password: z.string().max(128, "密码不能超过 128 个字符"),
  is_active: z.boolean(),
  is_superuser: z.boolean(),
  role_ids: z.array(z.string()),
});

export type UserFormValues = z.infer<typeof userFormSchema>;

type UserFormDialogProps = {
  user: User | null;
  roles: Role[];
  rolesLoading: boolean;
  canManageRoles: boolean;
  canManageSuperusers: boolean;
  currentUserId: string | undefined;
  onClose: () => void;
  onSubmit: (values: UserFormValues) => Promise<void>;
};

function getDefaultValues(user: User | null): UserFormValues {
  return {
    username: user?.username ?? "",
    email: user?.email ?? "",
    full_name: user?.full_name ?? "",
    password: "",
    is_active: user?.is_active ?? true,
    is_superuser: user?.is_superuser ?? false,
    role_ids: user?.roles.map((role) => role.id) ?? [],
  };
}

export function UserFormDialog({
  user,
  roles,
  rolesLoading,
  canManageRoles,
  canManageSuperusers,
  currentUserId,
  onClose,
  onSubmit,
}: UserFormDialogProps) {
  const isEditing = user !== null;
  const schema = useMemo(
    () =>
      userFormSchema.superRefine((values, context) => {
        if (!isEditing && values.password.length < 8) {
          context.addIssue({
            code: "custom",
            path: ["password"],
            message: "密码至少需要 8 个字符",
          });
        } else if (values.password.length > 0 && values.password.length < 8) {
          context.addIssue({
            code: "custom",
            path: ["password"],
            message: "密码至少需要 8 个字符",
          });
        }
      }),
    [isEditing],
  );
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<UserFormValues>({
    resolver: zodResolver(schema),
    defaultValues: getDefaultValues(user),
  });

  useEffect(() => {
    reset(getDefaultValues(user));
  }, [reset, user]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !isSubmitting) {
        onClose();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [isSubmitting, onClose]);

  async function submit(values: UserFormValues) {
    try {
      await onSubmit(values);
    } catch (error) {
      toast.error(getErrorMessage(error, "保存用户失败"));
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-slate-950/40 p-4 backdrop-blur-[1px] animate-in fade-in duration-150"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isSubmitting) {
          onClose();
        }
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-form-title"
        className="my-4 w-full max-w-2xl rounded-xl border border-border bg-card shadow-2xl animate-in zoom-in-95 duration-150"
      >
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            <h2 id="user-form-title" className="text-lg font-semibold">
              {isEditing ? "编辑用户" : "新增用户"}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {isEditing ? "更新账号资料、状态和角色。" : "创建可登录系统的新账号。"}
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={onClose}
            disabled={isSubmitting}
            aria-label="关闭用户表单"
          >
            <X />
          </Button>
        </div>

        <form onSubmit={handleSubmit(submit)}>
          <div className="grid gap-5 px-5 py-5 sm:grid-cols-2">
            <FormField label="用户名" error={errors.username?.message}>
              <Input
                {...register("username")}
                aria-invalid={Boolean(errors.username)}
                autoComplete="username"
                placeholder="请输入用户名"
              />
            </FormField>
            <FormField label="邮箱" error={errors.email?.message} hint="选填">
              <Input
                {...register("email")}
                aria-invalid={Boolean(errors.email)}
                type="email"
                autoComplete="email"
                placeholder="name@example.com"
              />
            </FormField>
            <FormField label="姓名" error={errors.full_name?.message}>
              <Input
                {...register("full_name")}
                aria-invalid={Boolean(errors.full_name)}
                autoComplete="name"
                placeholder="选填"
              />
            </FormField>
            <FormField
              label={isEditing ? "新密码" : "密码"}
              error={errors.password?.message}
              hint={isEditing ? "留空则保持原密码" : "至少 8 个字符"}
            >
              <Input
                {...register("password")}
                aria-invalid={Boolean(errors.password)}
                type="password"
                autoComplete="new-password"
                placeholder={isEditing ? "无需修改可留空" : "请输入密码"}
              />
            </FormField>

            <div className="sm:col-span-2">
              <div className="mb-2 text-sm font-medium">账号设置</div>
              <div className="grid gap-3 rounded-lg border border-border bg-muted/35 p-4 sm:grid-cols-2">
                <CheckboxField
                  label="启用账号"
                  description="禁用后该用户将无法登录系统。"
                  locked={user?.id === currentUserId}
                  inputProps={register("is_active")}
                />
                <CheckboxField
                  label="超级管理员"
                  description="拥有全部系统权限，请谨慎授予。"
                  locked={!canManageSuperusers || user?.id === currentUserId}
                  inputProps={register("is_superuser")}
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <div className="mb-2 text-sm font-medium">角色</div>
              <div className="grid gap-2 rounded-lg border border-border p-3 sm:grid-cols-2">
                {rolesLoading ? (
                  <div className="flex items-center gap-2 py-2 text-sm text-muted-foreground sm:col-span-2">
                    <Loader2 className="size-4 animate-spin" />
                    正在加载角色
                  </div>
                ) : !canManageRoles ? (
                  <p className="py-2 text-sm text-muted-foreground sm:col-span-2">
                    当前账号无法读取角色列表，本次保存不会修改已有角色。
                  </p>
                ) : roles.length === 0 ? (
                  <p className="py-2 text-sm text-muted-foreground sm:col-span-2">暂无可选角色。</p>
                ) : (
                  roles.map((role) => (
                    <label
                      key={role.id}
                      className="flex cursor-pointer items-start gap-3 rounded-md px-2 py-2 transition hover:bg-muted"
                    >
                      <input
                        {...register("role_ids")}
                        type="checkbox"
                        value={role.id}
                        className="mt-0.5 size-4 accent-primary"
                      />
                      <span className="min-w-0">
                        <span className="block text-sm font-medium">{role.name}</span>
                        <span className="block truncate text-xs text-muted-foreground">
                          {role.description || "暂无描述"}
                        </span>
                      </span>
                    </label>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 border-t border-border px-5 py-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              取消
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? <Loader2 className="animate-spin" /> : null}
              {isEditing ? "保存修改" : "创建用户"}
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}

function FormField({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block text-sm font-medium">
      <span className="mb-2 flex items-center justify-between gap-3">
        {label}
        {hint ? <span className="text-xs font-normal text-muted-foreground">{hint}</span> : null}
      </span>
      {children}
      {error ? (
        <span role="alert" className="mt-1.5 block text-xs font-normal text-destructive">
          {error}
        </span>
      ) : null}
    </label>
  );
}

function CheckboxField({
  label,
  description,
  locked,
  inputProps,
}: {
  label: string;
  description: string;
  locked?: boolean;
  inputProps: UseFormRegisterReturn;
}) {
  return (
    <label className={locked ? "flex items-start gap-3 opacity-60" : "flex items-start gap-3"}>
      <input
        {...inputProps}
        type="checkbox"
        aria-disabled={locked}
        tabIndex={locked ? -1 : undefined}
        onClick={locked ? (event) => event.preventDefault() : undefined}
        onKeyDown={
          locked
            ? (event) => {
                if (event.key === " ") {
                  event.preventDefault();
                }
              }
            : undefined
        }
        className={
          locked
            ? "mt-0.5 size-4 cursor-not-allowed accent-primary"
            : "mt-0.5 size-4 accent-primary"
        }
      />
      <span>
        <span className="block text-sm font-medium">{label}</span>
        <span className="mt-0.5 block text-xs text-muted-foreground">{description}</span>
      </span>
    </label>
  );
}
