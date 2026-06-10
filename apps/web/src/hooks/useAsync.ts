"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { isAbortError } from "@/lib/api";

type AsyncOperation<T> = (signal: AbortSignal) => Promise<T>;

type UseAsyncOptions<T> = {
  enabled?: boolean;
  initialData?: T | null;
};

export function useAsync<T>(
  operation: AsyncOperation<T>,
  { enabled = true, initialData = null }: UseAsyncOptions<T> = {},
) {
  const initialDataRef = useRef(initialData);
  initialDataRef.current = initialData;

  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<unknown>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setData(initialDataRef.current);
      setLoading(false);
      setError(null);
      return;
    }

    const controller = new AbortController();
    setData(initialDataRef.current);
    setLoading(true);
    setError(null);

    Promise.resolve()
      .then(() => operation(controller.signal))
      .then((result) => {
        if (!controller.signal.aborted) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((caughtError: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        if (isAbortError(caughtError)) {
          setLoading(false);
          return;
        }
        setError(caughtError);
        setLoading(false);
      });

    return () => controller.abort();
  }, [enabled, reloadKey, operation]);

  const reload = useCallback(() => {
    setReloadKey((value) => value + 1);
  }, []);

  return { data, loading, error, reload };
}
