import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Me } from "@/types/api";

interface AuthState {
  user: Me | null;
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: Me) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setUser: (user) => set({ user }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
    }),
    { name: "cf-auth", storage: createJSONStorage(() => localStorage) },
  ),
);
