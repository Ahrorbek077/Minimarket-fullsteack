import { api } from "@/lib/axios";

export type ReportType   = "sales" | "purchases" | "stock" | "top_products";
export type ReportFormat = "excel" | "pdf";

export const reportService = {
  async export(params: {
    file_format: ReportFormat;
    type:        ReportType;
    date_from:   string;
    date_to:     string;
    limit?:      number;
  }): Promise<Blob> {
    const { data } = await api.get("/reports/export/", {
      params,
      responseType: "blob",
    });
    return data;
  },

  async getSalesSummary(dateFrom: string, dateTo: string) {
    const { data } = await api.get("/reports/sales/summary/", {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return data.data;
  },

  async getSalesChart(dateFrom: string, dateTo: string, period = "daily") {
    const { data } = await api.get("/reports/sales/chart/", {
      params: { date_from: dateFrom, date_to: dateTo, period },
    });
    return data.data;
  },

  async getTopProducts(dateFrom: string, dateTo: string, limit = 10) {
    const { data } = await api.get("/reports/sales/top-products/", {
      params: { date_from: dateFrom, date_to: dateTo, limit },
    });
    return data.data;
  },

  async getStockSummary() {
    const { data } = await api.get("/reports/stock/summary/");
    return data.data;
  },

  async getDebts() {
    const { data } = await api.get("/reports/purchases/debts/");
    return data;
  },
};
