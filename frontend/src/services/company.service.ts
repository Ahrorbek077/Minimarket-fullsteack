import { api } from "@/lib/axios";
import type { Branch, Company, PaginatedResponse } from "@/types";

export const companyService = {
  async getAll(params?: Record<string, unknown>): Promise<PaginatedResponse<Company>> {
    const { data } = await api.get("/companies/", { params });
    return data;
  },
  async getById(id: number): Promise<Company & { branches: Branch[] }> {
    const { data } = await api.get(`/companies/${id}/`);
    return data.data;
  },
  async create(payload: Partial<Company>) {
    const { data } = await api.post("/companies/", payload);
    return data.data;
  },
  async update(id: number, payload: Partial<Company>) {
    const { data } = await api.patch(`/companies/${id}/`, payload);
    return data.data;
  },
  async delete(id: number) {
    await api.delete(`/companies/${id}/`);
  },
  async getBranches(companyId: number): Promise<Branch[]> {
    const { data } = await api.get(`/companies/${companyId}/branches/`);
    return data.results ?? data.data ?? [];
  },
  async createBranch(companyId: number, payload: Partial<Branch>) {
    const { data } = await api.post(`/companies/${companyId}/branches/`, payload);
    return data.data;
  },
  async updateBranch(companyId: number, branchId: number, payload: Partial<Branch>) {
    const { data } = await api.patch(`/companies/${companyId}/branches/${branchId}/update/`, payload);
    return data.data;
  },
  async deleteBranch(companyId: number, branchId: number) {
    await api.delete(`/companies/${companyId}/branches/${branchId}/delete/`);
  },
  async getBranchProducts(companyId: number, branchId: number): Promise<any[]> {
    const { data } = await api.get(`/companies/${companyId}/branches/${branchId}/products/`);
    return data.results ?? [];
  },
};
