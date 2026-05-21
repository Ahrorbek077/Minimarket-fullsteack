"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import {
  X, Plus, Pencil, Trash2, GitBranch,
  Loader2, Check, Package, ChevronRight,
} from "lucide-react";
import { companyService } from "@/services/company.service";
import { formatCurrency, cn } from "@/lib/utils";
import type { Branch, Company } from "@/types";

const branchSchema = z.object({
  name:    z.string().min(2, "Kamida 2 belgi"),
  phone:   z.string().optional(),
  address: z.string().optional(),
});
type BranchForm = z.infer<typeof branchSchema>;

interface Props {
  company: Company;
  onClose: () => void;
}

export function BranchesDrawer({ company, onClose }: Props) {
  const qc = useQueryClient();
  const [editBranch,   setEditBranch]   = useState<Branch | null | "new">(null);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);
  const [tab, setTab] = useState<"info" | "products">("info");

  const { data: branches, isLoading } = useQuery({
    queryKey: ["branches", company.id],
    queryFn:  () => companyService.getBranches(company.id),
  });

  const { data: branchProducts, isLoading: productsLoading } = useQuery({
    queryKey: ["branch-products", company.id, selectedBranch?.id],
    queryFn:  () => companyService.getBranchProducts(company.id, selectedBranch!.id),
    enabled:  !!selectedBranch && tab === "products",
  });

  const deleteMutation = useMutation({
    mutationFn: (branchId: number) => companyService.deleteBranch(company.id, branchId),
    onSuccess:  () => {
      qc.invalidateQueries({ queryKey: ["branches", company.id] });
      toast.success("Filial o'chirildi");
      if (selectedBranch) setSelectedBranch(null);
    },
    onError: (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-lg h-full bg-white dark:bg-slate-900 shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-brand-500" />
              <h2 className="font-semibold text-slate-800 dark:text-white">Filiallar</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{company.name}</p>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Branch detail view */}
        {selectedBranch ? (
          <div className="flex flex-col flex-1 min-h-0">
            {/* Branch detail header */}
            <div className="px-5 pt-4 pb-0 shrink-0">
              <button onClick={() => { setSelectedBranch(null); setTab("info"); }}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-brand-500 transition mb-3">
                ← Filiallar ro'yxati
              </button>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-brand-600/10 flex items-center justify-center shrink-0">
                  <GitBranch className="w-5 h-5 text-brand-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 dark:text-white">{selectedBranch.name}</h3>
                  {selectedBranch.phone && <p className="text-xs text-slate-400">{selectedBranch.phone}</p>}
                </div>
              </div>
              {/* Tabs */}
              <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 mb-4">
                {[
                  { id: "info" as const, label: "Ma'lumotlar" },
                  { id: "products" as const, label: "Mahsulotlar" },
                ].map(({ id, label }) => (
                  <button key={id} onClick={() => setTab(id)}
                    className={cn(
                      "flex-1 py-1.5 rounded-md text-xs font-medium transition",
                      tab === id
                        ? "bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm"
                        : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                    )}>
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto px-5 pb-5">
              {tab === "info" ? (
                <div className="space-y-3">
                  {selectedBranch.address && (
                    <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
                      <p className="text-xs text-slate-400 mb-0.5">Manzil</p>
                      <p className="text-sm text-slate-700 dark:text-slate-200">{selectedBranch.address}</p>
                    </div>
                  )}
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
                    <p className="text-xs text-slate-400 mb-0.5">Qo'shilgan</p>
                    <p className="text-sm text-slate-700 dark:text-slate-200">
                      {new Date(selectedBranch.created_at).toLocaleDateString("uz-UZ")}
                    </p>
                  </div>
                </div>
              ) : (
                /* Products tab */
                productsLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
                  </div>
                ) : !branchProducts || branchProducts.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-32 text-slate-400">
                    <Package className="w-7 h-7 mb-2 opacity-30" />
                    <p className="text-sm">Bu filialdan hali mahsulot xarid qilinmagan</p>
                    <p className="text-xs mt-1 text-slate-300">Xaridlar sahifasidan xarid qiling</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {branchProducts.map((product: any) => (
                      <div key={product.id}
                        className="flex items-center gap-3 px-3 py-2.5 bg-slate-50 dark:bg-slate-800 rounded-xl">
                        <div className="w-8 h-8 rounded-lg bg-brand-600/10 flex items-center justify-center shrink-0">
                          <Package className="w-4 h-4 text-brand-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-800 dark:text-white truncate">{product.name}</p>
                          <p className="text-xs text-slate-400">
                            {product.category_name ?? "—"} · {product.unit_short ?? ""}
                          </p>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                            {formatCurrency(product.sell_price)}
                          </p>
                          <p className={cn("text-xs", product.stock_qty > 0 ? "text-emerald-500" : "text-red-400")}>
                            {product.stock_qty} {product.unit_short ?? ""}
                          </p>
                        </div>
                      </div>
                    ))}
                    <p className="text-xs text-center text-slate-400 pt-2">
                      Jami {branchProducts.length} ta mahsulot
                    </p>
                  </div>
                )
              )}
            </div>
          </div>
        ) : (
          /* Branches list */
          <div className="flex-1 overflow-y-auto p-5 space-y-3">

            {/* Add new */}
            {editBranch === "new" ? (
              <BranchFormComp
                companyId={company.id}
                branch={null}
                onClose={() => setEditBranch(null)}
                onSaved={() => { qc.invalidateQueries({ queryKey: ["branches", company.id] }); setEditBranch(null); }}
              />
            ) : (
              <button onClick={() => setEditBranch("new")}
                className="w-full flex items-center gap-2 h-10 px-4 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 text-sm text-slate-400 hover:border-brand-400 hover:text-brand-500 transition">
                <Plus className="w-4 h-4" />
                Yangi filial qo'shish
              </button>
            )}

            {/* List */}
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
              </div>
            ) : branches?.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-slate-400">
                <GitBranch className="w-7 h-7 mb-2 opacity-30" />
                <p className="text-sm">Hali filial yo'q</p>
              </div>
            ) : (
              branches?.map((branch) =>
                editBranch && (editBranch as Branch).id === branch.id ? (
                  <BranchFormComp
                    key={branch.id}
                    companyId={company.id}
                    branch={branch}
                    onClose={() => setEditBranch(null)}
                    onSaved={() => { qc.invalidateQueries({ queryKey: ["branches", company.id] }); setEditBranch(null); }}
                  />
                ) : (
                  <div key={branch.id}
                    className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 flex items-start justify-between group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700/60 transition"
                    onClick={() => setSelectedBranch(branch)}>
                    <div className="flex items-start gap-3 min-w-0 flex-1">
                      <div className="w-8 h-8 rounded-lg bg-brand-600/10 flex items-center justify-center shrink-0 mt-0.5">
                        <GitBranch className="w-4 h-4 text-brand-600" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-slate-800 dark:text-white text-sm">{branch.name}</p>
                        {branch.phone   && <p className="text-xs text-slate-400 mt-0.5">{branch.phone}</p>}
                        {branch.address && <p className="text-xs text-slate-400 truncate">{branch.address}</p>}
                      </div>
                    </div>
                    <div className="flex gap-1 items-center shrink-0 ml-2">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                        <button
                          onClick={(e) => { e.stopPropagation(); setEditBranch(branch); }}
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-brand-500 hover:bg-white dark:hover:bg-slate-600 transition">
                          <Pencil className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); if (window.confirm("O'chirishni tasdiqlaysizmi?")) deleteMutation.mutate(branch.id); }}
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-white dark:hover:bg-slate-600 transition">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-brand-500 transition" />
                    </div>
                  </div>
                )
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function BranchFormComp({ companyId, branch, onClose, onSaved }: {
  companyId: number;
  branch:    Branch | null;
  onClose:   () => void;
  onSaved:   () => void;
}) {
  const isEdit = !!branch;
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<BranchForm>({
    resolver: zodResolver(branchSchema),
    defaultValues: {
      name:    branch?.name    ?? "",
      phone:   branch?.phone   ?? "",
      address: branch?.address ?? "",
    },
  });

  const onSubmit = async (data: BranchForm) => {
    setSaving(true);
    try {
      if (isEdit) await companyService.updateBranch(companyId, branch!.id, data);
      else        await companyService.createBranch(companyId, data);
      toast.success(isEdit ? "Filial yangilandi" : "Filial qo'shildi");
      onSaved();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-brand-50 dark:bg-brand-950/20 border border-brand-200 dark:border-brand-800 rounded-xl p-4 space-y-3">
      <p className="text-xs font-semibold text-brand-700 dark:text-brand-400">
        {isEdit ? "Filialni tahrirlash" : "Yangi filial"}
      </p>

      <div>
        <input {...register("name")} placeholder="Filial nomi *"
          className={cn(
            "w-full h-9 px-3 rounded-lg border text-sm focus:outline-none focus:ring-1 transition bg-white dark:bg-slate-800",
            errors.name
              ? "border-red-400 focus:ring-red-400"
              : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
          )}
          autoFocus
        />
        {errors.name && <p className="mt-1 text-xs text-red-400">{errors.name.message}</p>}
      </div>

      <input {...register("phone")} placeholder="Telefon"
        className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />

      <input {...register("address")} placeholder="Manzil"
        className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />

      <div className="flex gap-2 pt-1">
        <button type="button" onClick={onClose}
          className="flex-1 h-8 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-white dark:hover:bg-slate-800 transition">
          Bekor
        </button>
        <button
          type="button"
          onClick={handleSubmit(onSubmit)}
          disabled={saving}
          className="flex-1 h-8 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium flex items-center justify-center gap-1.5 transition disabled:opacity-50">
          {saving
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <><Check className="w-3.5 h-3.5" />{isEdit ? "Saqlash" : "Qo'shish"}</>
          }
        </button>
      </div>
    </div>
  );
}
