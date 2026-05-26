"use client";

import { useEffect } from "react";
import axios from "axios";

export function ServerWakeup() {
  useEffect(() => {
    const base = (process.env.NEXT_PUBLIC_API_URL ?? "").replace("/api/v1", "");
    if (base) axios.get(`${base}/health`, { timeout: 60_000 }).catch(() => {});
  }, []);
  return null;
}
