"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import {
  X, ArrowUpDown, Loader2, Check,
  TrendingUp, TrendingDown, Equal,
} from "lucide-react";
import { inventoryService } from "@/services/inventory.service";
import { formatCurrency, cn } from "@/lib/utils";
import type { Stock } from "@/services/inventory.service";

const schema = z.object({
  type:     z.enum(["add", "remove", "set"]),
  quantity: z.string().min(1, "Miqdor kiriting"),
  reason:   z.string().min(3, "Sabab kiriting (kamida 3 belgi)"),
});
type FormData = z.infer<typeof schema>;

interface Props {
  stock:   Stock;
  onClose: () => void;
  onSaved: () => void;
}

export function AdjustModal({ stock, onClose, onSaved }: Props) {
  const [saving, setSaving] = useState(false);
  const currentQty = parseFloat(stock.quantity);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { type: "add", quantity: "", reason: "" },
  });

  const type     = watch("type");
  const quantity = parseFloat(watch("quantity") || "0");

  // Preview new quantity
  const newQty =
    type === "add"    ? currentQty + quantity :
    type === "remove" ? currentQty - quantity :
    quantity;

  const previewColor =
    newQty < 0                                ? "text-red-500" :
    newQty <= parseFloat(stock.min_stock)     ? "text-amber-500" :
    "text-emerald-600";

  const REASONS: Record<string, string[]> = {
    add:    ["Yangi qabul", "Inventarizatsiya to'g'irlash", "Qaytarilgan tovar"],
    remove: ["Yaroqsiz tovar", "Inventarizatsiya yo'qotish", "Boshqa do'konga o'tkazish"],
    set:    ["Inventarizatsiya natijasi", "Boshlang'ich qoldiq"],
  };

  const onSubmit = async (data: FormData) => {
    if (newQty < 0) { toast.error("Yangi qoldiq 0 dan kam bo'lishi mumkin emas"); return; }
    setSaving(true);
    try {
      const finalQty =
        data.type === "add"    ? String(currentQty + parseFloat(data.quantity)) :
        data.type === "remove" ? String(currentQty - parseFloat(data.quantity)) :
        data.quantity;

      await inventoryService.adjust({
        product_id: stock.product_id,
        quantity:   finalQty,
        reason:     data.reason,
      });
      toast.success("Qoldiq yangilandi");
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

      <div className="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-4 h-4 text-brand-500" />
            <h2 className="font-semibold text-slate-800 dark:text-white">Qoldiqni o'zgartirish</h2>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">

          {/* Product info */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
            <p className="font-medium text-slate-800 dark:text-white text-sm">{stock.product_name}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
              <span>Joriy qoldiq: <strong className="text-slate-700 dark:text-slate-200">{currentQty} {stock.unit_short}</strong></span>
              <span>Min: <strong>{stock.min_stock} {stock.unit_short}</strong></span>
            </div>
          </div>

          {/* Operation type */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-2 block">Amal turi</label>
            <div className="grid grid-cols-3 gap-2">
              {([
                { value: "add"    as const, label: "Qo'shish",   Icon: TrendingUp,   cls: "text-emerald-600" },
                { value: "remove" as const, label: "Ayirish",    Icon: TrendingDown, cls: "text-red-500"     },
                { value: "set"    as const, label: "O'rnatish",  Icon: Equal,        cls: "text-blue-500"    },
              ]).map(({ value, label, Icon, cls }) => (
                <label key={value}
                  className={cn(
                    "flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 cursor-pointer transition",
                    type === value
                      ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
                      : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                  )}>
                  <input {...register("type")} type="radio" value={value} className="sr-only" />
                  <Icon className={cn("w-4 h-4", type === value ? "text-brand-600" : cls)} />
                  <span className={cn("text-xs font-medium", type === value ? "text-brand-700 dark:text-brand-400" : "text-slate-600 dark:text-slate-400")}>
                    {label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Quantity */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">
              Miqdor *
              {type !== "set" && <span className="ml-1 text-slate-400">(dona yoki kg)</span>}
            </label>
            <input
              {...register("quantity")}
              type="number" min="0.01" step="0.01"
              placeholder={type === "set" ? "Yangi qoldiq miqdori" : "Miqdor kiriting"}
              className={cn(
                "w-full h-10 px-4 rounded-xl border text-sm focus:outline-none focus:ring-1 transition",
                "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
                errors.quantity
                  ? "border-red-400 focus:ring-red-400"
                  : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
              )}
              autoFocus
            />
            {errors.quantity && <p className="mt-1 text-xs text-red-400">{errors.quantity.message}</p>}
          </div>

          {/* Preview */}
          {quantity > 0 && (
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-xl text-sm">
              <span className="text-slate-500">Natija:</span>
              <span className={cn("font-bold text-base", previewColor)}>
                {newQty.toFixed(2)} {stock.unit_short}
              </span>
            </div>
          )}

          {/* Reason */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">Sabab *</label>
            <input
              {...register("reason")}
              placeholder="O'zgarish sababini kiriting..."
              list={`reasons-${type}`}
              className={cn(
                "w-full h-10 px-4 rounded-xl border text-sm focus:outline-none focus:ring-1 transition",
                "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
                errors.reason
                  ? "border-red-400 focus:ring-red-400"
                  : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
              )}
            />
            {/* Datalist for quick reasons */}
            <datalist id={`reasons-${type}`}>
              {(REASONS[type] ?? []).map((r) => <option key={r} value={r} />)}
            </datalist>
            {errors.reason && <p className="mt-1 text-xs text-red-400">{errors.reason.message}</p>}
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button type="submit" disabled={saving || (newQty < 0 && type !== "set")}
              className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-brand-600/20">
              {saving
                ? <><Loader2 className="w-4 h-4 animate-spin" />Saqlanmoqda...</>
                : <><Check className="w-4 h-4" />Saqlash</>
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
