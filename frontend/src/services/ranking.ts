import { api } from "@/lib/api";
import type { Algo, RankingResponse } from "@/types/api";

export const rankingService = {
  async rank(body: {
    job_title: string;
    job_description: string;
    resume_ids: string[];
    algorithms: Algo[];
    explain_top_k?: number;
  }) {
    const { data } = await api.post<RankingResponse>("/ranking", body);
    return data;
  },

  async rankFiles(params: {
    files: File[];
    job_title: string;
    job_description: string;
    algorithms: Algo[];
    explain_top_k?: number;
  }) {
    const fd = new FormData();
    params.files.forEach((f) => fd.append("files", f));
    fd.append("job_title", params.job_title);
    fd.append("job_description", params.job_description);
    fd.append("algorithms", params.algorithms.join(","));
    if (params.explain_top_k != null) {
      fd.append("explain_top_k", String(params.explain_top_k));
    }
    const { data } = await api.post<RankingResponse>("/ranking/upload", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};
