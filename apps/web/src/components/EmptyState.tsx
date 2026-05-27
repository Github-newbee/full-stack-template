import { Inbox } from "lucide-react";

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="grid min-h-64 place-items-center rounded-lg border border-dashed border-border bg-card p-8 text-center">
      <div>
        <div className="mx-auto mb-4 flex size-10 items-center justify-center rounded-md bg-muted">
          <Inbox className="size-5 text-muted-foreground" />
        </div>
        <h2 className="font-semibold">{title}</h2>
        <p className="mt-2 max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
