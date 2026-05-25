import { api } from "@/lib/api";
import type { Me, TokenPair } from "@/types/api";

export const authService = {
  async register(data: { email: string; password: string; full_name: string; role?: string }) {
    const { data: res } = await api.post<TokenPair>("/auth/register", data);
    return res;
  },
  async login(data: { email: string; password: string }) {
    const { data: res } = await api.post<TokenPair>("/auth/login", data);
    return res;
  },
  async me() {
    const { data } = await api.get<Me>("/auth/me");
    return data;
  },
};
