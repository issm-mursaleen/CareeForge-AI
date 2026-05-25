import { api } from "@/lib/api";
import type { InterviewSession, AnswerResult } from "@/types/api";

export const interviewService = {
  async generate(resumeId: string, role: string, count = 5): Promise<InterviewSession> {
    const { data } = await api.post<InterviewSession>("/interview/generate", {
      resume_id: resumeId,
      role,
      count,
    });
    return data;
  },

  async answer(
    interviewId: string,
    questionIndex: number,
    answer: string,
  ): Promise<AnswerResult> {
    const { data } = await api.post<AnswerResult>(`/interview/${interviewId}/answer`, {
      question_index: questionIndex,
      answer,
    });
    return data;
  },
};
