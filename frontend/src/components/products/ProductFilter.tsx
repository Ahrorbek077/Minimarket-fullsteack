"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, SlidersHorizontal } from "lucide-react";
import { productService } from "@/services/product.service";
import { cn } from "@/lib/utils";

interface Props {
  filters:  Record<string, any>;
  onApply:  (f: Record<string, any>) => void;
  onClose:  () => void;
}

export function ProductFilter({ filters, onApply, onClose }: Props) {
  const [local, setLocal] = useState({ ...filters });

  const { data: categories } = useQuery({
    queryKey: ["categories"], queryFn: productService.getCategories, staleTime: Infinity,
  });

  const set = (key: string, val: any) =>
    setLocal((prev) => val === "" || val === undefined ? (({ [key]: _, ...rest }) => rest)(prev) : { ...prev, [key]: val });

  const handleReset = () => setLocal({});

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">

        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-brand-500" />
            <h3 className="font-semibold text-slate-800 dark:text-white text-sm">Filtr</h3>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Category */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">Kategoriya</label>
            <select value={local.category_id ?? ""} onChange={(e) => set("category_id", e.target.value || undefined)}
              className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition">
              <option value="">Barchasi</option>
              {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          {/* Active */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">Holat</label>
            <div className="flex gap-2">
              {[
                { val: undefined,  label: "Barchasi" },
                { val: "true",     label: "Faol"     },
                { val: "false",    label: "Nofaol"   },
              ].map(({ val, label }) => (
                <button key={label} type="button"
                  onClick={() => set("is_active", val)}
                  className={cn(
                    "flex-1 py-1.5 rounded-lg border text-xs font-medium transition",
                    String(local.is_active) === String(val) || (val === undefined && local.is_active === undefined)
                      ? "bg-brand-600 text-white border-brand-600"
                      : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-brand-400"
                  )}>
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Low stock */}
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative">
              <input type="checkbox" className="sr-only peer"
                checked={!!local.low_stock}
                onChange={(e) => set("low_stock", e.target.checked ? "true" : undefined)} />
              <div className="w-9 h-5 rounded-full bg-slate-200 dark:bg-slate-700 peer-checked:bg-brand-600 transition-colors" />
              <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
            </div>
            <span className="text-sm text-slate-600 dark:text-slate-300">Faqat kam qoldiqlar</span>
          </label>

          {/* Price range */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-500 mb-1.5 block">Min narx</label>
              <input type="number" min="0" value={local.min_price ?? ""} placeholder="0"
                onChange={(e) => set("min_price", e.target.value || undefined)}
                className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500 mb-1.5 block">Max narx</label>
              <input type="number" min="0" value={local.max_price ?? ""} placeholder="∞"
                onChange={(e) => set("max_price", e.target.value || undefined)}
                className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 pb-5 flex gap-3">
          <button onClick={handleReset}
            className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
            Tozalash
          </button>
          <button onClick={() => onApply(local)}
            className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition shadow-sm shadow-brand-600/20">
            Qo'llash {Object.keys(local).length > 0 && `(${Object.keys(local).length})`}
          </button>
        </div>
      </div>
    </div>
  );
}
