"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { X, Loader2, ImagePlus, Barcode, RefreshCw } from "lucide-react";
import { productService } from "@/services/product.service";
import { cn } from "@/lib/utils";
import type { Product } from "@/types";

const schema = z.object({
  name:        z.string().min(1, "Nomi majburiy"),
  barcode:     z.string().optional(),
  category_id: z.string().optional(),
  unit_id:     z.string().optional(),
  cost_price:  z.string().min(1, "Tan narxi majburiy"),
  sell_price:  z.string().min(1, "Sotish narxi majburiy"),
  min_stock:   z.string().optional(),
  description: z.string().optional(),
  is_active:   z.boolean(),
});
type FormData = z.infer<typeof schema>;

interface Props {
  product: Product | null;
  onClose: () => void;
  onSaved: () => void;
}

// Tasodifiy barcode generator (EAN-13 format)
function generateBarcode(): string {
  const digits = Array.from({ length: 12 }, () => Math.floor(Math.random() * 10));
  const sum    = digits.reduce((acc, d, i) => acc + (i % 2 === 0 ? d : d * 3), 0);
  const check  = (10 - (sum % 10)) % 10;
  return [...digits, check].join("");
}

export function ProductModal({ product, onClose, onSaved }: Props) {
  const isEdit = !!product;
  const [saving, setSaving] = useState(false);

  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: productService.getCategories, staleTime: Infinity });
  const { data: units }      = useQuery({ queryKey: ["units"],      queryFn: productService.getUnits,      staleTime: Infinity });

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name:        product?.name       ?? "",
      barcode:     product?.barcode    ?? "",
      category_id: "",
      unit_id:     "",
      cost_price:  product?.cost_price ?? "",
      sell_price:  product?.sell_price ?? "",
      min_stock:   "0",
      description: "",
      is_active:   product?.is_active  ?? true,
    },
  });

  const costPrice  = parseFloat(watch("cost_price") || "0");
  const sellPrice  = parseFloat(watch("sell_price") || "0");
  const margin     = costPrice > 0 ? ((sellPrice - costPrice) / costPrice * 100).toFixed(1) : "0";

  const onSubmit = async (data: any) => {
    setSaving(true);
    try {
      const payload = {
        ...data,
        category_id: data.category_id ? parseInt(data.category_id) : undefined,
        unit_id:     data.unit_id     ? parseInt(data.unit_id)     : undefined,
        cost_price:  parseFloat(data.cost_price),
        sell_price:  parseFloat(data.sell_price),
        min_stock:   parseFloat(data.min_stock || "0"),
      };
      if (isEdit) await productService.updateProduct(product.id, payload);
      else        await productService.createProduct(payload);
      toast.success(isEdit ? "Mahsulot yangilandi" : "Mahsulot qo'shildi");
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
      <div className="relative w-full max-w-xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="font-semibold text-slate-800 dark:text-white">
            {isEdit ? "Mahsulotni tahrirlash" : "Yangi mahsulot"}
          </h2>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">

            {/* Name */}
            <Field label="Nomi *" error={errors.name?.message}>
              <input {...register("name")} placeholder="Mahsulot nomi"
                className={inputCls(!!errors.name)} />
            </Field>

            {/* Barcode */}
            <Field label="Barcode">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Barcode className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input {...register("barcode")} placeholder="Barcode raqami"
                    className={cn(inputCls(false), "pl-9")} />
                </div>
                <button type="button"
                  onClick={() => setValue("barcode", generateBarcode())}
                  className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center gap-1.5
                    text-xs text-slate-500 hover:text-brand-600 hover:border-brand-400 transition shrink-0">
                  <RefreshCw className="w-3.5 h-3.5" />
                  Yaratish
                </button>
              </div>
            </Field>

            {/* Category + Unit */}
            <div className="grid grid-cols-2 gap-3">
              <Field label="Kategoriya">
                <select {...register("category_id")} className={inputCls(false)}>
                  <option value="">— tanlang —</option>
                  {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </Field>
              <Field label="O'lchov birligi">
                <select {...register("unit_id")} className={inputCls(false)}>
                  <option value="">— tanlang —</option>
                  {units?.map((u) => <option key={u.id} value={u.id}>{u.name} ({u.short_name})</option>)}
                </select>
              </Field>
            </div>

            {/* Prices */}
            <div className="grid grid-cols-2 gap-3">
              <Field label="Tan narxi *" error={errors.cost_price?.message}>
                <input {...register("cost_price")} type="number" min="0" step="0.01"
                  placeholder="0.00" className={inputCls(!!errors.cost_price)} />
              </Field>
              <Field label="Sotish narxi *" error={errors.sell_price?.message}>
                <input {...register("sell_price")} type="number" min="0" step="0.01"
                  placeholder="0.00" className={inputCls(!!errors.sell_price)} />
              </Field>
            </div>

            {/* Margin indicator */}
            {costPrice > 0 && sellPrice > 0 && (
              <div className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium",
                parseFloat(margin) < 0   ? "bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400"
                : parseFloat(margin) < 10 ? "bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400"
                : "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400"
              )}>
                Foyda marginali: <strong>{margin}%</strong>
                {parseFloat(margin) < 0 && " — sotish narxi tan narxidan past!"}
              </div>
            )}

            {/* Min stock */}
            <Field label="Minimum qoldiq (ogohlantirish)">
              <input {...register("min_stock")} type="number" min="0" step="0.01"
                placeholder="5" className={inputCls(false)} />
            </Field>

            {/* Description */}
            <Field label="Tavsif">
              <textarea {...register("description")} rows={2} placeholder="Mahsulot haqida..."
                className={cn(inputCls(false), "resize-none")} />
            </Field>

            {/* Active */}
            <label className="flex items-center gap-3 cursor-pointer">
              <div className="relative">
                <input {...register("is_active")} type="checkbox" className="sr-only peer" />
                <div className="w-9 h-5 rounded-full bg-slate-200 dark:bg-slate-700 peer-checked:bg-brand-600 transition-colors" />
                <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
              </div>
              <span className="text-sm text-slate-600 dark:text-slate-300">Faol mahsulot</span>
            </label>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex gap-3">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button type="submit" disabled={saving}
              className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-60 shadow-sm shadow-brand-600/20">
              {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saqlanmoqda...</> : isEdit ? "Saqlash" : "Qo'shish"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-500 mb-1.5">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  );
}

function inputCls(hasError: boolean) {
  return cn(
    "w-full h-9 px-3 rounded-lg border text-sm focus:outline-none focus:ring-1 transition",
    "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
    hasError
      ? "border-red-400 focus:border-red-400 focus:ring-red-400"
      : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
  );
}
