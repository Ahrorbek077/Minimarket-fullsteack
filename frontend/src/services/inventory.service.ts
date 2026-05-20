import { api } from "@/lib/axios";
import type { PaginatedResponse } from "@/types";

export interface Stock {
  id:              number;
  product_id:      number;
  product_name:    string;
  product_barcode: string | null;
  unit_short:      string;
  category_name:   string | null;
  quantity:        string;
  min_stock:       string;
  cost_price:      string;
  sell_price:      string;
  cost_value:      string;
  sell_value:      string;
  is_low:          boolean;
  updated_at:      string;
}

export interface StockMovement {
  id:          number;
  product_name:string;
  type:        "in" | "out" | "adjustment";
  quantity:    string;
  reason:      string;
  source_type: string;
  created_by:  string | null;
  created_at:  string;
}

export interface AdjustInput {
  product_id: number;
  quantity:   string;
  reason:     string;
}

export const inventoryService = {
  async getStocks(params?: Record<string, unknown>): Promise<PaginatedResponse<Stock>> {
    const { data } = await api.get("/inventory/stocks/", { params });
    return data;
  },
  async getMovements(params?: Record<string, unknown>): Promise<PaginatedResponse<StockMovement>> {
    const { data } = await api.get("/inventory/movements/", { params });
    return data;
  },
  async adjust(payload: AdjustInput) {
    const { data } = await api.post("/inventory/adjust/", payload);
    return data.data;
  },
};
