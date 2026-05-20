import { api } from "@/lib/axios";
import type { AuthTokens, User } from "@/types";

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const { data } = await api.post("/auth/login/", { email, password });
    return data;
  },

  async logout(refresh: string): Promise<void> {
    await api.post("/auth/logout/", { refresh });
  },

  async refreshToken(refresh: string) {
    const { data } = await api.post("/auth/token/refresh/", { refresh });
    return data;
  },

  async getMe(): Promise<User> {
    const { data } = await api.get("/auth/me/profile/");
    return data.data;
  },

  async updateProfile(payload: Partial<User>): Promise<User> {
    const { data } = await api.patch("/auth/me/update_profile/", payload);
    return data.data;
  },

  async changePassword(old_password: string, new_password: string, new_password_confirm: string) {
    await api.post("/auth/me/change-password/", {
      old_password, new_password, new_password_confirm,
    });
  },
};
