import { api } from "@/lib/axios";
import type { PaginatedResponse, User, UserRole } from "@/types";

export interface CreateUserPayload {
  email:      string;
  full_name:  string;
  phone?:     string;
  role:       UserRole;
  password:   string;
}

export interface UpdateUserPayload {
  full_name?: string;
  phone?:     string;
  role?:      UserRole;
}

export const staffService = {
  async getAll(params?: Record<string, unknown>): Promise<PaginatedResponse<User>> {
    const { data } = await api.get("/auth/users/", { params });
    return data;
  },

  async create(payload: CreateUserPayload): Promise<User> {
    const { data } = await api.post("/auth/users/", payload);
    return data.data;
  },

  async update(id: number, payload: UpdateUserPayload): Promise<User> {
    const { data } = await api.patch(`/auth/users/${id}/`, payload);
    return data.data;
  },

  async softDelete(id: number): Promise<void> {
    await api.delete(`/auth/users/${id}/`);
  },

  async resetPassword(id: number, new_password: string): Promise<void> {
    await api.post(`/auth/users/${id}/reset-password/`, { new_password });
  },
};
