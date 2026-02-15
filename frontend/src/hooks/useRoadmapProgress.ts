import { useEffect, useRef, useState } from "react";
import { getRoadmapWsUrl } from "../services/api";
import type { CourseRoadmap } from "../types/chat";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export type RoadmapStatus =
  | "idle"
  | "connecting"
  | "pending"
  | "in_progress"
  | "completed"
  | "error";

export interface RoadmapProgress {
  /** Current high-level status. */
  status: RoadmapStatus;
  /** Machine-readable step label, e.g. "analysing_answers". */
  step: string;
  /** Human-readable detail message for the UI. */
  detail: string;
  /** 0-100 completion percentage. */
  progressPct: number;
  /** The completed roadmap (only set when status === "completed"). */
  roadmap: CourseRoadmap | null;
  /** Error message if status === "error". */
  error: string | null;
}

const INITIAL_STATE: RoadmapProgress = {
  status: "idle",
  step: "",
  detail: "",
  progressPct: 0,
  roadmap: null,
  error: null,
};

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

/**
 * React hook that connects to the backend WebSocket for a given session
 * and streams roadmap generation progress.
 *
 * - Automatically reconnects on transient failures (up to 5 attempts).
 * - On reconnect the server re-sends the latest cached state so the UI
 *   picks up where it left off.
 * - The connection is torn down when `sessionId` is null / changes.
 */
export function useRoadmapProgress(sessionId: string | null): RoadmapProgress {
  const [state, setState] = useState<RoadmapProgress>(INITIAL_STATE);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const MAX_RETRIES = 5;

  useEffect(() => {
    // Reset on session change (deferred to avoid cascading render)
    queueMicrotask(() => setState(INITIAL_STATE));
    retriesRef.current = 0;

    if (!sessionId) return;

    function connect() {
      const sid = sessionId;
      if (!sid) return;

      setState((s) => ({ ...s, status: "connecting" }));

      const url = getRoadmapWsUrl(sid);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        retriesRef.current = 0;
        setState((s) => ({
          ...s,
          status: s.status === "connecting" ? "pending" : s.status,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setState({
            status: data.status ?? "in_progress",
            step: data.step ?? "",
            detail: data.detail ?? "",
            progressPct: data.progress_pct ?? 0,
            roadmap: data.roadmap ?? null,
            error: data.status === "error" ? data.detail : null,
          });
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = (event) => {
        // If the server closed normally after completion, don't reconnect
        if (event.code === 1000) return;

        // Auth failure
        if (event.code === 4001) {
          setState((s) => ({
            ...s,
            status: "error",
            error: "Authentication failed. Please log in again.",
          }));
          return;
        }

        // Attempt reconnect with exponential backoff
        if (retriesRef.current < MAX_RETRIES) {
          const delay = Math.min(1000 * 2 ** retriesRef.current, 16000);
          retriesRef.current += 1;
          setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // onclose will fire right after — handled there
      };
    }

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [sessionId]);

  return state;
}
