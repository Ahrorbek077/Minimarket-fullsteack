import { api } from "@/lib/axios";
import type { DashboardData, PeriodStats } from "@/types";

export const dashboardService = {
  async getDashboard(chartDays = 7, topLimit = 5): Promise<DashboardData> {
    const { data } = await api.get("/dashboard/", {
      params: { chart_days: chartDays, top_limit: topLimit },
    });
    return data.data;
  },

  async getPeriodStats(period: "today" | "week" | "month" | "year"): Promise<PeriodStats> {
    const { data } = await api.get("/dashboard/period/", { params: { period } });
    return data.data;
  },
};
