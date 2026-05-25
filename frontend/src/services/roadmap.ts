import { api } from "@/lib/api";
import type { RoadmapPlan } from "@/types/api";

export const roadmapService = {
  async create(resumeId: string, targetRole: string): Promise<RoadmapPlan> {
    const { data } = await api.post<RoadmapPlan>("/roadmap", {
      resume_id: resumeId,
      target_role: targetRole,
    });
    return data;
  },

  async list(): Promise<RoadmapPlan[]> {
    const { data } = await api.get<RoadmapPlan[]>("/roadmap");
    return data;
  },
};
