import { api } from "@/lib/api";
import type { AnalyticsSummary, MLPerformance } from "@/types/api";

export const analyticsService = {
  async summary() {
    const { data } = await api.get<AnalyticsSummary>("/analytics/summary");
    return data;
  },
  async mlPerformance() {
    const { data } = await api.get<MLPerformance>("/analytics/ml-performance");
    return data;
  },
};
