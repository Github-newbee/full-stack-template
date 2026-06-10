"use client";

import { Loader2, TriangleAlert, X } from "lucide-react";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import type { User } from "@/lib/types";

export function DeleteUserDialog({
  user,
  deleting,
  onClose,
  onConfirm,
}: {
  user: User;
  deleting: boolean;
  onClose: () => void;
  onConfirm: () => void;
}) {
  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !deleting) {
        onClose();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [deleting, onClose]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-[1px] animate-in fade-in duration-150"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !deleting) {
          onClose();
        }
      }}
    >
      <section
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-user-title"
        aria-describedby="delete-user-description"
        className="w-full max-w-md rounded-xl border border-border bg-card shadow-2xl animate-in zoom-in-95 duration-150"
      >
        <div className="flex items-start justify-between gap-4 px-5 pt-5">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-red-50 text-destructive">
            <TriangleAlert className="size-5" />
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={onClose}
            disabled={deleting}
            aria-label="关闭删除确认"
          >
            <X />
          </Button>
        </div>
        <div className="px-5 py-4">
          <h2 id="delete-user-title" className="text-lg font-semibold">
            删除用户
          </h2>
          <p id="delete-user-description" className="mt-2 text-sm text-muted-foreground">
            确定删除用户“{user.username}”吗？此操作不可撤销。
          </p>
        </div>
        <div className="flex justify-end gap-3 border-t border-border px-5 py-4">
          <Button type="button" variant="outline" onClick={onClose} disabled={deleting}>
            取消
          </Button>
          <Button type="button" variant="destructive" onClick={onConfirm} disabled={deleting}>
            {deleting ? <Loader2 className="animate-spin" /> : null}
            确认删除
          </Button>
        </div>
      </section>
    </div>
  );
}
