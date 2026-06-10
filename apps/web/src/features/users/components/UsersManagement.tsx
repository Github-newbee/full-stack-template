"use client";

import { type ColumnDef, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Loader2, Pencil, Plus, RefreshCw, Trash2 } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { DataPagination } from "@/components/ui/pagination";
import { listRoles } from "@/features/roles/api";
import { useAsync } from "@/hooks/useAsync";
import { useAsyncAction } from "@/hooks/useAsyncAction";
import { getErrorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { PageResponse, Role, User } from "@/lib/types";
import { buildUserPayload, createUser, deleteUser, listUsers, updateUser } from "../api";
import { canReadRoles, canWriteUsers, getPermissionCodes } from "../permissions";
import { DeleteUserDialog } from "./DeleteUserDialog";
import { UserFormDialog, type UserFormValues } from "./UserFormDialog";

const EMPTY_USERS: User[] = [];
const EMPTY_ROLES: Role[] = [];
const USERS_PAGE_SIZE = 20;

type UserDialogState =
  | {
      mode: "create";
    }
  | {
      mode: "edit";
      user: User;
    };

export function UsersManagement() {
  const { user: currentUser, refreshUser } = useAuth();
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<UserDialogState | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);

  const permissions = useMemo(() => getPermissionCodes(currentUser), [currentUser]);
  const canWrite = canWriteUsers(currentUser, permissions);
  const canReadRoleList = canReadRoles(currentUser, permissions);

  const loadUsers = useCallback(
    (signal: AbortSignal) => listUsers({ page, pageSize: USERS_PAGE_SIZE, signal }),
    [page],
  );
  const loadRoles = useCallback((signal: AbortSignal) => listRoles({ signal }), []);
  const usersQuery = useAsync<PageResponse<User>>(loadUsers);
  const rolesQuery = useAsync<Role[]>(loadRoles, {
    enabled: canReadRoleList,
    initialData: EMPTY_ROLES,
  });

  const data = usersQuery.data;
  const roles = rolesQuery.data ?? EMPTY_ROLES;
  const loadFailed = usersQuery.error !== null;
  const rolesLoadFailed = rolesQuery.error !== null;
  const canManageRoles = canReadRoleList && !rolesLoadFailed;

  const columns = useMemo<ColumnDef<User>[]>(() => {
    const tableColumns: ColumnDef<User>[] = [
      {
        accessorKey: "username",
        header: "用户名",
        cell: ({ row }) => (
          <div>
            <div className="font-medium">{row.original.username}</div>
            {row.original.is_superuser ? (
              <div className="mt-0.5 text-xs text-primary">超级管理员</div>
            ) : null}
          </div>
        ),
      },
      {
        accessorKey: "email",
        header: "邮箱",
        cell: ({ row }) => row.original.email || "-",
      },
      {
        accessorKey: "full_name",
        header: "姓名",
        cell: ({ row }) => row.original.full_name || "-",
      },
      {
        accessorKey: "is_active",
        header: "状态",
        cell: ({ row }) => (
          <span
            className={
              row.original.is_active
                ? "inline-flex rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700"
                : "inline-flex rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground"
            }
          >
            {row.original.is_active ? "启用" : "禁用"}
          </span>
        ),
      },
      {
        id: "roles",
        accessorFn: (user) => user.roles.map((role) => role.name).join(", "),
        header: "角色",
        cell: ({ getValue }) => (getValue<string>() ? getValue<string>() : "-"),
      },
    ];

    if (canWrite) {
      tableColumns.push({
        id: "actions",
        header: "操作",
        cell: ({ row }) => {
          const target = row.original;
          const canManageTarget = Boolean(currentUser?.is_superuser || !target.is_superuser);
          const canDeleteTarget = canManageTarget && target.id !== currentUser?.id;

          return (
            <div className="flex items-center gap-1">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                onClick={() => setDialog({ mode: "edit", user: target })}
                disabled={!canManageTarget}
                aria-label={`编辑用户 ${target.username}`}
                title={canManageTarget ? "编辑" : "只有超级管理员可以管理超级管理员"}
              >
                <Pencil />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="text-destructive hover:bg-red-50 hover:text-destructive"
                onClick={() => setDeleteTarget(target)}
                disabled={!canDeleteTarget}
                aria-label={`删除用户 ${target.username}`}
                title={
                  target.id === currentUser?.id
                    ? "不能删除当前登录账号"
                    : canDeleteTarget
                      ? "删除"
                      : "只有超级管理员可以管理超级管理员"
                }
              >
                <Trash2 />
              </Button>
            </div>
          );
        },
      });
    }

    return tableColumns;
  }, [canWrite, currentUser]);

  const table = useReactTable({
    data: data?.items ?? EMPTY_USERS,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getRowId: (row) => row.id,
    manualPagination: true,
  });

  const saveUserAction = useAsyncAction(async (values: UserFormValues) => {
    if (dialog?.mode === "edit") {
      const payload = buildUserPayload({
        values,
        canManageRoles,
        canManageSuperusers: Boolean(currentUser?.is_superuser),
        includeEmptyRoles: false,
      });
      const updatedUser = await updateUser(dialog.user.id, payload);

      if (updatedUser.id === currentUser?.id) {
        await refreshUser();
      }
      toast.success("用户信息已更新");
    } else {
      const payload = buildUserPayload({
        values,
        canManageRoles,
        canManageSuperusers: Boolean(currentUser?.is_superuser),
        includeEmptyRoles: true,
      });

      await createUser(payload);
      setPage(1);
      toast.success("用户已创建");
    }

    setDialog(null);
    usersQuery.reload();
    rolesQuery.reload();
  });

  async function confirmDeleteUser() {
    if (!deleteTarget) {
      return;
    }

    try {
      await deleteUserAction.execute(deleteTarget.id);
      const shouldGoToPreviousPage = page > 1 && data?.items.length === 1;
      setDeleteTarget(null);
      toast.success("用户已删除");
      if (shouldGoToPreviousPage) {
        setPage((value) => value - 1);
      } else {
        usersQuery.reload();
      }
    } catch (error) {
      toast.error(getErrorMessage(error, "删除用户失败"));
    }
  }

  const deleteUserAction = useAsyncAction(deleteUser);

  function reload() {
    usersQuery.reload();
    rolesQuery.reload();
  }

  const formUser = dialog?.mode === "edit" ? dialog.user : null;

  return (
    <>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={reload}
          disabled={usersQuery.loading}
        >
          <RefreshCw className={usersQuery.loading ? "animate-spin" : undefined} />
          刷新
        </Button>
        {canWrite ? (
          <Button
            type="button"
            size="sm"
            onClick={() => setDialog({ mode: "create" })}
            aria-label="新增用户"
          >
            <Plus />
            <span className="hidden sm:inline">新增用户</span>
          </Button>
        ) : null}
      </div>

      {usersQuery.loading && !data ? (
        <div className="grid min-h-64 place-items-center rounded-lg border border-border bg-card">
          <Loader2 className="size-6 animate-spin text-primary" aria-label="加载用户数据" />
        </div>
      ) : loadFailed ? (
        <div>
          <EmptyState title="用户数据加载失败" description="请稍后重试或检查 API 服务状态。" />
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState title="暂无用户" description="点击“新增用户”创建第一个账号。" />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border bg-card">
          <table className="w-full min-w-200 text-left text-sm">
            <thead className="bg-muted text-muted-foreground">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="px-4 py-2 font-medium">
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-t border-border transition hover:bg-muted/40">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && !loadFailed ? (
        <DataPagination
          page={page}
          total={data.total}
          pageSize={data.page_size}
          onPageChange={setPage}
        />
      ) : null}

      {dialog ? (
        <UserFormDialog
          user={formUser}
          roles={roles}
          rolesLoading={rolesQuery.loading}
          canManageRoles={canManageRoles}
          canManageSuperusers={Boolean(currentUser?.is_superuser)}
          currentUserId={currentUser?.id}
          onClose={() => setDialog(null)}
          onSubmit={saveUserAction.execute}
        />
      ) : null}

      {deleteTarget ? (
        <DeleteUserDialog
          user={deleteTarget}
          deleting={deleteUserAction.pending}
          onClose={() => setDeleteTarget(null)}
          onConfirm={confirmDeleteUser}
        />
      ) : null}
    </>
  );
}
