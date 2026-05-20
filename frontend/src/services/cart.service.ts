import { api } from "@/lib/axios";
import type { Cart } from "@/types";

export const cartService = {
  async getCart(): Promise<Cart> {
    const { data } = await api.get("/sales/cart/cart/");
    return data.data;
  },

  async addItem(product_id: number, quantity = 1): Promise<Cart> {
    const { data } = await api.post("/sales/cart/add/", { product_id, quantity });
    return data.data;
  },

  async scan(barcode: string, quantity = 1): Promise<Cart> {
    const { data } = await api.post("/sales/cart/scan/", { barcode, quantity });
    return data.data;
  },

  async updateItem(product_id: number, quantity: number): Promise<Cart> {
    const { data } = await api.patch(`/sales/cart/update/${product_id}/`, { quantity });
    return data.data;
  },

  async removeItem(product_id: number): Promise<Cart> {
    const { data } = await api.delete(`/sales/cart/remove/${product_id}/`);
    return data.data;
  },

  async clear(): Promise<void> {
    await api.delete("/sales/cart/clear/");
  },

  async checkout(payments: { method: string; amount: string }[], discount_pct = 0, note = "") {
    const { data } = await api.post("/sales/checkout/", { payments, discount_pct, note });
    return data;
  },
};
