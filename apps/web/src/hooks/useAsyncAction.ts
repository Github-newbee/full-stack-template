"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type AsyncAction<Arguments extends unknown[], Result> = (...args: Arguments) => Promise<Result>;

export function useAsyncAction<Arguments extends unknown[], Result>(
  action: AsyncAction<Arguments, Result>,
) {
  const actionRef = useRef(action);
  actionRef.current = action;

  const mountedRef = useRef(true);
  const pendingCountRef = useRef(0);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...args: Arguments): Promise<Result> => {
    pendingCountRef.current += 1;
    setPending(true);
    setError(null);

    try {
      return await actionRef.current(...args);
    } catch (caughtError) {
      if (mountedRef.current) {
        setError(caughtError);
      }
      throw caughtError;
    } finally {
      pendingCountRef.current -= 1;
      if (mountedRef.current && pendingCountRef.current === 0) {
        setPending(false);
      }
    }
  }, []);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  return { execute, pending, error, resetError };
}
