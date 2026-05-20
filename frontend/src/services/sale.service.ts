import { api } from "@/lib/axios";
import type { PaginatedResponse, Sale } from "@/types";

export interface SaleDetail extends Sale {
  items: {
    id:                  number;
    product_name:        string;
    product_barcode:     string | null;
    unit_short:          string;
    quantity:            string;
    sell_price:          string;
    cost_price_snapshot: string;
    total:               string;
  }[];
  payments: {
    id:     number;
    method: string;
    amount: string;
  }[];
  note: string;
}

export const saleService = {
  async getAll(params?: Record<string, unknown>): Promise<PaginatedResponse<Sale>> {
    const { data } = await api.get("/sales/", { params });
    return data;
  },
  async getById(id: number): Promise<SaleDetail> {
    const { data } = await api.get(`/sales/${id}/`);
    return data.data;
  },
  async returnSale(id: number, reason = "") {
    const { data } = await api.post(`/sales/${id}/return/`, { reason });
    return data.data;
  },
  async getDailySummary(date?: string) {
    const { data } = await api.get("/sales/daily-summary/", {
      params: date ? { date } : undefined,
    });
    return data.data;
  },
};

export interface DailySummary {
  date:          string;
  total_sales:   number;
  total_revenue: string | number;
  total_cash:    string | number;
  total_card:    string | number;
  total_debt:    string | number;
}
