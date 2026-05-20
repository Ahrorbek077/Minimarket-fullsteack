import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
  user:         User | null;
  accessToken:  string | null;
  refreshToken: string | null;   // DEPRECATED: cookie da saqlangan, saqlab qolindi compat uchun
  isAuth:       boolean;
  setAuth:      (user: User, access: string, refresh?: string) => void;
  setUser:      (user: User) => void;
  setToken:     (access: string) => void;
  logout:       () => void;
}

/** Middleware cookie — SSR redirect uchun (httpOnly emas, faqat mavjudlik belgisi) */
function setPresenceCookie(value: string | null) {
  if (typeof document === "undefined") return;
  if (value) {
    // access_token_present: qisqa muddatli (30 daqiqa), httpOnly emas (middleware o'qiydi)
    document.cookie = `access_token_present=1; path=/; max-age=1800; SameSite=Lax`;
  } else {
    document.cookie = `access_token_present=; path=/; max-age=0`;
  }
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user:         null,
      accessToken:  null,
      refreshToken: null,
      isAuth:       false,

      setAuth: (user, access, refresh) => {
        // access_token — memory (Zustand) da saqlash yetarli
        // refresh_token — backend httpOnly cookie da
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", access);
        }
        setPresenceCookie(access);
        set({ user, accessToken: access, isAuth: true });
      },

      setToken: (access) => {
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", access);
        }
        setPresenceCookie(access);
        set({ accessToken: access });
      },

      setUser: (user) => set({ user }),

      logout: () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
        }
        setPresenceCookie(null);
        set({ user: null, accessToken: null, refreshToken: null, isAuth: false });
      },
    }),
    {
      name: "auth-store",
      partialize: (s) => ({
        user:        s.user,
        accessToken: s.accessToken,
        isAuth:      s.isAuth,
      }),
    }
  )
);
