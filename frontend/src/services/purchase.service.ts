import { api } from "@/lib/axios";
import type { PaginatedResponse, Purchase } from "@/types";

export interface PurchaseItemInput {
  product_id: number;
  quantity:   string;
  cost_price: string;
  sell_price: string;
}

export interface CreatePurchaseInput {
  company_id:  number;
  branch_id?:  number | null;
  invoice_no?: string;
  due_date?:   string | null;
  note?:       string;
  items:       PurchaseItemInput[];
}

export const purchaseService = {
  async getAll(params?: Record<string, unknown>): Promise<PaginatedResponse<Purchase>> {
    const { data } = await api.get("/purchases/", { params });
    return data;
  },
  async getById(id: number): Promise<Purchase> {
    const { data } = await api.get(`/purchases/${id}/`);
    return data;
  },
  async create(payload: CreatePurchaseInput) {
    const { data } = await api.post("/purchases/", payload);
    return data.data;
  },
  async receive(id: number) {
    const { data } = await api.post(`/purchases/${id}/receive/`);
    return data.data;
  },
  async pay(id: number, amount: string, note = "") {
    const { data } = await api.post(`/purchases/${id}/pay/`, { amount, note });
    return data;
  },
  async cancel(id: number, reason = "") {
    const { data } = await api.post(`/purchases/${id}/cancel/`, { reason });
    return data;
  },
  async getDebts() {
    const { data } = await api.get("/purchases/debts/");
    return data;
  },
  async getOverdue() {
    const { data } = await api.get("/purchases/overdue/");
    return data;
  },
};
