import { api } from "@/lib/api";
import type { ResumeAnalysis, ResumeListItem } from "@/types/api";

export const resumeService = {
  async analyze(file: File, jobDescription?: string) {
    const fd = new FormData();
    fd.append("file", file);
    if (jobDescription) fd.append("job_description", jobDescription);
    const { data } = await api.post<ResumeAnalysis>("/resumes/analyze", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
  async list() {
    const { data } = await api.get<ResumeListItem[]>("/resumes");
    return data;
  },
  async get(id: string) {
    const { data } = await api.get<ResumeAnalysis>(`/resumes/${id}`);
    return data;
  },
};
