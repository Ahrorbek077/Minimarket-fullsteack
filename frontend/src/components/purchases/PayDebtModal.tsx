"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import { X, Banknote, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { purchaseService } from "@/services/purchase.service";
import { formatCurrency, cn } from "@/lib/utils";
import type { Purchase } from "@/types";

const schema = z.object({
  amount: z.string().min(1, "Summa kiriting"),
  note:   z.string().optional(),
});
type FormData = z.infer<typeof schema>;

interface Props {
  purchase: Purchase;
  onClose:  () => void;
  onPaid:   () => void;
}

export function PayDebtModal({ purchase, onClose, onPaid }: Props) {
  const debt     = parseFloat(purchase.debt_amount);
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { amount: purchase.debt_amount },
  });

  const amount    = parseFloat(watch("amount") || "0");
  const isPartial = amount < debt;
  const isOver    = amount > debt;

  const onSubmit = async (data: FormData) => {
    setSaving(true);
    try {
      await purchaseService.pay(purchase.id, data.amount, data.note);
      toast.success(isPartial
        ? `${formatCurrency(amount)} to'landi — qoldi: ${formatCurrency(debt - amount)}`
        : "Qarz to'liq to'landi"
      );
      onPaid();
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
            <Banknote className="w-4 h-4 text-emerald-500" />
            <h2 className="font-semibold text-slate-800 dark:text-white">Qarz to'lash</h2>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">

          {/* Purchase info */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Kompaniya</span>
              <span className="font-medium text-slate-800 dark:text-white">{purchase.company_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Faktura</span>
              <span className="font-mono text-slate-700 dark:text-slate-200">{purchase.invoice_no}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Jami summa</span>
              <span className="text-slate-700 dark:text-slate-200">{formatCurrency(purchase.total_amount)}</span>
            </div>
            <div className="flex justify-between border-t border-slate-200 dark:border-slate-700 pt-2 mt-2">
              <span className="text-slate-500 font-medium">Qarz qoldiq</span>
              <span className="font-bold text-red-500 text-base">{formatCurrency(purchase.debt_amount)}</span>
            </div>
          </div>

          {/* Amount input */}
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1.5">
              To'lov miqdori *
            </label>
            <div className="relative">
              <input
                {...register("amount")}
                type="number"
                min="0.01"
                step="0.01"
                className={cn(
                  "w-full h-11 px-4 pr-12 rounded-xl border text-sm focus:outline-none focus:ring-1 transition",
                  "bg-white dark:bg-slate-800 text-slate-800 dark:text-white",
                  errors.amount
                    ? "border-red-400 focus:border-red-400 focus:ring-red-400"
                    : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
                )}
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400">
                so'm
              </span>
            </div>
            {errors.amount && <p className="mt-1 text-xs text-red-400">{errors.amount.message}</p>}

            {/* Quick fill buttons */}
            <div className="flex gap-2 mt-2">
              {[0.25, 0.5, 0.75, 1].map((pct) => (
                <button
                  key={pct}
                  type="button"
                  onClick={() => {
                    const val = (debt * pct).toFixed(2);
                    (document.querySelector('input[type="number"]') as HTMLInputElement).value = val;
                  }}
                  className="flex-1 py-1 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:border-brand-400 hover:text-brand-600 transition"
                >
                  {pct === 1 ? "To'liq" : `${pct * 100}%`}
                </button>
              ))}
            </div>
          </div>

          {/* Status indicator */}
          {amount > 0 && (
            <div className={cn(
              "flex items-center gap-2 p-3 rounded-xl border text-sm",
              isOver
                ? "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400"
                : isPartial
                ? "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400"
                : "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400"
            )}>
              {isOver
                ? <AlertCircle className="w-4 h-4 shrink-0" />
                : <CheckCircle2 className="w-4 h-4 shrink-0" />
              }
              {isOver
                ? `To'lov qarzdan ${formatCurrency(amount - debt)} ko'p — ortiqcha qabul qilinmaydi`
                : isPartial
                ? `Qisman to'lov — qoladi: ${formatCurrency(debt - amount)}`
                : "Qarz to'liq yopiladi"
              }
            </div>
          )}

          {/* Note */}
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1.5">Izoh</label>
            <input
              {...register("note")}
              placeholder="To'lov haqida izoh..."
              className="w-full h-9 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition"
            />
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={saving || amount <= 0}
              className="flex-1 h-10 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-emerald-600/20"
            >
              {saving
                ? <><Loader2 className="w-4 h-4 animate-spin" />To'lanmoqda...</>
                : <><Banknote className="w-4 h-4" />To'lash</>
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
