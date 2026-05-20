import { api } from "@/lib/axios";
import type { PaginatedResponse } from "@/types";

export interface AuditLog {
  id:          number;
  user_email:  string | null;
  user_name:   string | null;
  action:      string;
  action_display: string;
  model_name:  string;
  object_id:   number | null;
  object_repr: string;
  extra:       Record<string, any>;
  ip_address:  string | null;
  created_at:  string;
}

export const historyService = {
  async getLogs(params?: Record<string, unknown>): Promise<PaginatedResponse<AuditLog>> {
    const { data } = await api.get("/history/logs/", { params });
    return data;
  },
};
