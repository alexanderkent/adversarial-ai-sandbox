import { useCallback, useState } from "react";
import { defendAttack, runAttack, type Params, type RunResult } from "../api";

export function useRun(attackId: string | null) {
  const [result, setResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (mode: "run" | "defend", params: Params) => {
      if (!attackId) return;
      setLoading(true);
      setError(null);
      try {
        const fn = mode === "defend" ? defendAttack : runAttack;
        setResult(await fn(attackId, params));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Request failed");
      } finally {
        setLoading(false);
      }
    },
    [attackId],
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, execute, reset };
}
