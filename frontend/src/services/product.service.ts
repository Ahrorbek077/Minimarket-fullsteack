import { api } from "@/lib/axios";
import type { Category, PaginatedResponse, Product, Unit } from "@/types";

export const productService = {
  async getProducts(params?: Record<string, unknown>): Promise<PaginatedResponse<Product>> {
    const { data } = await api.get("/products/products/", { params });
    return data;
  },

  async getProduct(id: number): Promise<Product> {
    const { data } = await api.get(`/products/products/${id}/`);
    return data;
  },

  async getByBarcode(barcode: string): Promise<Product> {
    const { data } = await api.get(`/products/products/barcode/${barcode}/`);
    return data.data;
  },

  async createProduct(payload: FormData | Record<string, unknown>): Promise<Product> {
    const { data } = await api.post("/products/products/", payload);
    return data;
  },

  async updateProduct(id: number, payload: Record<string, unknown>): Promise<Product> {
    const { data } = await api.patch(`/products/products/${id}/`, payload);
    return data;
  },

  async deleteProduct(id: number): Promise<void> {
    await api.delete(`/products/products/${id}/`);
  },

  async getCategories(): Promise<Category[]> {
    const { data } = await api.get("/products/categories/");
    return data.results ?? data;
  },

  async getCategoryTree(): Promise<Category[]> {
    const { data } = await api.get("/products/categories/tree/");
    return data.data;
  },

  async getUnits(): Promise<Unit[]> {
    const { data } = await api.get("/products/units/");
    return data.results ?? data;
  },
};
