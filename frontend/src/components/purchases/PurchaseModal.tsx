"use client";
import { useState, useCallback } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  X, Plus, Trash2, Loader2, Search,
  Building2, Package, ChevronDown,
} from "lucide-react";
import { purchaseService } from "@/services/purchase.service";
import { productService  } from "@/services/product.service";
import { formatCurrency, cn } from "@/lib/utils";

// ─── Schema ───────────────────────────────────────────────────────────────────
const itemSchema = z.object({
  product_id:  z.number().min(1, "Mahsulot tanlang"),
  product_name:z.string(),
  quantity:    z.string().min(1, "Kiriting"),
  cost_price:  z.string().min(1, "Kiriting"),
  sell_price:  z.string().min(1, "Kiriting"),
});

const schema = z.object({
  company_id:  z.number().min(1, "Kompaniya tanlang"),
  company_name:z.string(),
  branch_id:   z.number().optional(),
  invoice_no:  z.string().optional(),
  due_date:    z.string().optional(),
  note:        z.string().optional(),
  items:       z.array(itemSchema).min(1, "Kamida 1 ta mahsulot"),
});
type FormData = z.infer<typeof schema>;

interface Props { onClose: () => void; onSaved: () => void; }

export function PurchaseModal({ onClose, onSaved }: Props) {
  const [saving,        setSaving]        = useState(false);
  const [productSearch, setProductSearch] = useState("");
  const [showCompany,   setShowCompany]   = useState(false);
  const [showProduct,   setShowProduct]   = useState(false);

  const { register, handleSubmit, control, watch, setValue, formState: { errors } } =
    useForm<FormData>({
      resolver: zodResolver(schema),
      defaultValues: { items: [] },
    });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  // Queries
  const { data: companies } = useQuery({
    queryKey: ["companies-list"],
    queryFn:  async () => {
      const { api } = await import("@/lib/axios");
      const { data } = await api.get("/companies/", { params: { page_size: 100 } });
      return data.results ?? [];
    },
    staleTime: 60_000,
  });

  const { data: products } = useQuery({
    queryKey: ["products-purchase", productSearch],
    queryFn:  () => productService.getProducts({ search: productSearch || undefined, page_size: 20, is_active: true }),
    enabled:  showProduct,
  });

  const selectedCompanyId = watch("company_id");
  const items             = watch("items");
  const totalAmount       = items.reduce(
    (sum, item) => sum + (parseFloat(item.quantity || "0") * parseFloat(item.cost_price || "0")),
    0
  );

  const addProduct = (product: any) => {
    const existing = fields.findIndex((f) => f.product_id === product.id);
    if (existing >= 0) {
      const cur = parseFloat(items[existing].quantity) || 1;
      setValue(`items.${existing}.quantity`, String(cur + 1));
    } else {
      append({
        product_id:   product.id,
        product_name: product.name,
        quantity:     "1",
        cost_price:   product.cost_price,
        sell_price:   product.sell_price,
      });
    }
    setShowProduct(false);
    setProductSearch("");
  };

  const onSubmit = async (data: FormData) => {
    setSaving(true);
    try {
      await purchaseService.create({
        company_id:  data.company_id,
        branch_id:   data.branch_id ?? null,
        invoice_no:  data.invoice_no,
        due_date:    data.due_date || null,
        note:        data.note,
        items:       data.items.map((i) => ({
          product_id:  i.product_id,
          quantity:    i.quantity,
          cost_price:  i.cost_price,
          sell_price:  i.sell_price,
        })),
      });
      toast.success("Xarid yaratildi");
      onSaved();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato yuz berdi");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <h2 className="font-semibold text-slate-800 dark:text-white">Yangi xarid</h2>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col flex-1 min-h-0">
          <div className="flex-1 overflow-y-auto p-6 space-y-5">

            {/* Company selector */}
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1.5">Kompaniya *</label>
              <div className="relative">
                <button type="button" onClick={() => setShowCompany(!showCompany)}
                  className={cn(
                    "w-full h-10 px-4 rounded-xl border text-sm text-left flex items-center justify-between transition",
                    "focus:outline-none focus:border-brand-500",
                    errors.company_id
                      ? "border-red-400 bg-white dark:bg-slate-800"
                      : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800"
                  )}>
                  <span className={watch("company_name") ? "text-slate-800 dark:text-white" : "text-slate-400"}>
                    {watch("company_name") || "Kompaniya tanlang..."}
                  </span>
                  <Building2 className="w-4 h-4 text-slate-400 shrink-0" />
                </button>

                {showCompany && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-lg z-10 max-h-48 overflow-y-auto">
                    {companies?.length === 0 && (
                      <p className="px-4 py-3 text-sm text-slate-400">Kompaniya topilmadi</p>
                    )}
                    {companies?.map((c: any) => (
                      <button key={c.id} type="button"
                        onClick={() => { setValue("company_id", c.id); setValue("company_name", c.name); setShowCompany(false); }}
                        className="w-full px-4 py-2.5 text-left text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 transition">
                        <p className="font-medium">{c.name}</p>
                        {c.phone && <p className="text-xs text-slate-400">{c.phone}</p>}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {errors.company_id && <p className="mt-1 text-xs text-red-400">Kompaniya tanlang</p>}
            </div>

            {/* Invoice + Due date */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1.5">Faktura raqami</label>
                <input {...register("invoice_no")} placeholder="INV-2024-001"
                  className="w-full h-10 px-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1.5">To'lov muddati</label>
                <input {...register("due_date")} type="date"
                  className="w-full h-10 px-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
              </div>
            </div>

            {/* Items header */}
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                Mahsulotlar
                {fields.length > 0 && (
                  <span className="ml-2 px-1.5 py-0.5 rounded-full bg-brand-100 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 text-xs">
                    {fields.length}
                  </span>
                )}
              </h3>
              <button type="button" onClick={() => setShowProduct(!showProduct)}
                className="flex items-center gap-1.5 h-8 px-3 rounded-lg bg-brand-50 dark:bg-brand-950/30 text-brand-600 dark:text-brand-400 text-xs font-medium hover:bg-brand-100 transition">
                <Plus className="w-3.5 h-3.5" />
                Mahsulot qo'shish
              </button>
            </div>

            {/* Product search dropdown */}
            {showProduct && (
              <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                <div className="relative border-b border-slate-200 dark:border-slate-700">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    autoFocus
                    value={productSearch}
                    onChange={(e) => setProductSearch(e.target.value)}
                    placeholder="Mahsulot nomi yoki barcode..."
                    className="w-full h-10 pl-9 pr-4 bg-white dark:bg-slate-800 text-sm focus:outline-none"
                  />
                </div>
                <div className="max-h-44 overflow-y-auto bg-white dark:bg-slate-800">
                  {products?.results.map((prod) => (
                    <button key={prod.id} type="button" onClick={() => addProduct(prod)}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition">
                      <Package className="w-4 h-4 text-slate-400 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{prod.name}</p>
                        <p className="text-xs text-slate-400">{formatCurrency(prod.cost_price)} · Qoldiq: {prod.stock_qty}</p>
                      </div>
                    </button>
                  ))}
                  {products?.results.length === 0 && (
                    <p className="px-4 py-3 text-sm text-slate-400">Topilmadi</p>
                  )}
                </div>
              </div>
            )}

            {/* Items list */}
            {fields.length > 0 ? (
              <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
                      <th className="px-3 py-2 text-left text-xs text-slate-500 font-medium">Mahsulot</th>
                      <th className="px-3 py-2 text-left text-xs text-slate-500 font-medium w-20">Miqdor</th>
                      <th className="px-3 py-2 text-left text-xs text-slate-500 font-medium w-24">Tan narxi</th>
                      <th className="px-3 py-2 text-left text-xs text-slate-500 font-medium w-24">Sotish narxi</th>
                      <th className="px-3 py-2 text-right text-xs text-slate-500 font-medium w-24">Jami</th>
                      <th className="w-8" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {fields.map((field, idx) => {
                      const qty   = parseFloat(items[idx]?.quantity  || "0");
                      const cost  = parseFloat(items[idx]?.cost_price || "0");
                      const subtotal = qty * cost;
                      return (
                        <tr key={field.id} className="bg-white dark:bg-slate-900">
                          <td className="px-3 py-2 text-xs font-medium text-slate-700 dark:text-slate-200 max-w-[160px] truncate">
                            {field.product_name}
                          </td>
                          <td className="px-3 py-2">
                            <input {...register(`items.${idx}.quantity`)} type="number" min="0.01" step="0.01"
                              className="w-16 h-7 px-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-right focus:outline-none focus:border-brand-500" />
                          </td>
                          <td className="px-3 py-2">
                            <input {...register(`items.${idx}.cost_price`)} type="number" min="0" step="0.01"
                              className="w-20 h-7 px-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-right focus:outline-none focus:border-brand-500" />
                          </td>
                          <td className="px-3 py-2">
                            <input {...register(`items.${idx}.sell_price`)} type="number" min="0" step="0.01"
                              className="w-20 h-7 px-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-right focus:outline-none focus:border-brand-500" />
                          </td>
                          <td className="px-3 py-2 text-right text-xs font-semibold text-slate-700 dark:text-slate-200">
                            {formatCurrency(subtotal)}
                          </td>
                          <td className="px-2 py-2">
                            <button type="button" onClick={() => remove(idx)}
                              className="w-6 h-6 rounded-lg flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition">
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>

                {/* Total row */}
                <div className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-700">
                  <span className="text-xs text-slate-500">{fields.length} ta mahsulot</span>
                  <span className="text-sm font-bold text-slate-800 dark:text-white">{formatCurrency(totalAmount)}</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-24 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 text-slate-400">
                <Package className="w-6 h-6 mb-1.5 opacity-50" />
                <p className="text-xs">Mahsulot qo'shing</p>
              </div>
            )}
            {errors.items && (
              <p className="text-xs text-red-400">{errors.items.message ?? errors.items.root?.message}</p>
            )}

            {/* Note */}
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1.5">Izoh</label>
              <textarea {...register("note")} rows={2} placeholder="Xarid haqida izoh..."
                className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 resize-none transition" />
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex gap-3 shrink-0">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button type="submit" disabled={saving || fields.length === 0}
              className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-brand-600/20">
              {saving
                ? <><Loader2 className="w-4 h-4 animate-spin" />Saqlanmoqda...</>
                : <>Xarid yaratish — {formatCurrency(totalAmount)}</>
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
