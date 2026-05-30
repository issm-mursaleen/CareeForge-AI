import { api } from "@/lib/api";
import type { GoodFitMetrics, GoodFitMetricsSummary } from "@/types/api";

export const mlService = {
  async getMLMetrics(limit = 20): Promise<GoodFitMetricsSummary[]> {
    const { data } = await api.get<GoodFitMetricsSummary[]>(
      `/ml/metrics?limit=${limit}`,
    );
    return data;
  },

  async getLatestMLMetrics(): Promise<GoodFitMetrics> {
    const { data } = await api.get<GoodFitMetrics>("/ml/latest");
    return data;
  },

  async retrainModel(): Promise<{ status: string; message: string }> {
    const { data } = await api.post<{ status: string; message: string }>(
      "/ml/retrain",
    );
    return data;
  },
};
