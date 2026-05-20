"use client";
import { useState, useEffect } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import {
  X, Banknote, CreditCard, Wallet, Plus, Trash2,
  ChevronRight, Loader2, CheckCircle2, AlertCircle,
} from "lucide-react";
import { cartService } from "@/services/cart.service";
import { formatCurrency, cn } from "@/lib/utils";
import type { Cart, PaymentMethod, Sale } from "@/types";

const schema = z.object({
  payments: z.array(z.object({
    method: z.enum(["cash", "card", "debt"]),
    amount: z.string().min(1),
  })).min(1),
  discount_pct: z.string(),
  note:         z.string().optional(),
});
type FormData = z.infer<typeof schema>;

const METHOD_CONFIG: Record<PaymentMethod, { label: string; Icon: any; color: string }> = {
  cash: { label: "Naqd",   Icon: Banknote,    color: "emerald" },
  card: { label: "Karta",  Icon: CreditCard,  color: "blue"    },
  debt: { label: "Nasiya", Icon: Wallet,       color: "amber"  },
};

interface Props {
  cart:    Cart;
  onClose: () => void;
  onDone:  (sale: Sale) => void;
}

export function CheckoutModal({ cart, onClose, onDone }: Props) {
  const total     = parseFloat(cart.total_amount);
  const [step,    setStep]    = useState<"payment" | "confirm">("payment");
  const [loading, setLoading] = useState(false);

  const { register, control, watch, setValue, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      payments:     [{ method: "cash", amount: cart.total_amount }],
      discount_pct: "0",
      note:         "",
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "payments" });
  const payments    = watch("payments");
  const discountPct = parseFloat(watch("discount_pct") || "0");
  const discount    = total * discountPct / 100;
  const netTotal    = total - discount;
  const paidTotal   = payments.reduce((s: number, p: FormData["payments"][0]) => s + (parseFloat(p.amount) || 0), 0);
  const remaining   = netTotal - paidTotal;
  const change      = paidTotal > netTotal ? paidTotal - netTotal : 0;

  // Chegirma o'zgarganda birinchi to'lovni yangilash
  useEffect(() => {
    if (fields.length === 1) {
      setValue("payments.0.amount", netTotal.toFixed(2));
    }
  }, [discountPct]);

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const result = await cartService.checkout(
        data.payments.map((p) => ({ method: p.method, amount: p.amount })),
        parseFloat(data.discount_pct || "0"),
        data.note || "",
      );
      toast.success(`Sotuv yakunlandi! Chek: ${result.data.invoice_no}`);
      onDone(result.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="font-semibold text-slate-800 dark:text-white">To'lov</h2>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400
              hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="p-6 space-y-5 max-h-[70vh] overflow-y-auto">

            {/* Order summary */}
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 space-y-2 text-sm">
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>{cart.item_count} ta mahsulot</span>
                <span>{formatCurrency(total)}</span>
              </div>
              {discountPct > 0 && (
                <div className="flex justify-between text-emerald-600">
                  <span>Chegirma ({discountPct}%)</span>
                  <span>−{formatCurrency(discount)}</span>
                </div>
              )}
              <div className="flex justify-between font-bold text-slate-800 dark:text-white border-t border-slate-200 dark:border-slate-700 pt-2 mt-2">
                <span>Jami</span>
                <span className="text-lg">{formatCurrency(netTotal)}</span>
              </div>
            </div>

            {/* Discount */}
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5 block">
                Chegirma %
              </label>
              <div className="flex gap-2">
                {[0, 5, 10, 15, 20].map((pct) => (
                  <button
                    key={pct}
                    type="button"
                    onClick={() => setValue("discount_pct", String(pct))}
                    className={cn(
                      "flex-1 py-1.5 rounded-lg border text-xs font-medium transition",
                      discountPct === pct
                        ? "bg-brand-600 text-white border-brand-600"
                        : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-brand-400"
                    )}
                  >
                    {pct === 0 ? "Yo'q" : `${pct}%`}
                  </button>
                ))}
                <input
                  {...register("discount_pct")}
                  type="number" min="0" max="100"
                  className="w-16 px-2 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700
                    bg-white dark:bg-slate-800 text-xs text-center focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>

            {/* Payment methods */}
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2 block">
                To'lov usuli
              </label>
              <div className="space-y-2">
                {fields.map((field, idx) => {
                  const method = payments[idx]?.method as PaymentMethod;
                  const cfg    = METHOD_CONFIG[method] || METHOD_CONFIG.cash;

                  return (
                    <div key={field.id} className="flex items-center gap-2">
                      {/* Method selector */}
                      <div className="flex gap-1 shrink-0">
                        {(["cash", "card", "debt"] as PaymentMethod[]).map((m) => {
                          const c = METHOD_CONFIG[m];
                          return (
                            <button
                              key={m}
                              type="button"
                              onClick={() => setValue(`payments.${idx}.method`, m)}
                              className={cn(
                                "flex items-center gap-1 px-2.5 py-1.5 rounded-lg border text-xs font-medium transition",
                                method === m
                                  ? "bg-brand-600 text-white border-brand-600"
                                  : "border-slate-200 dark:border-slate-700 text-slate-500 hover:border-brand-400"
                              )}
                            >
                              <c.Icon className="w-3 h-3" />
                              {c.label}
                            </button>
                          );
                        })}
                      </div>

                      {/* Amount */}
                      <input
                        {...register(`payments.${idx}.amount`)}
                        type="number" step="0.01" min="0"
                        className="flex-1 h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700
                          bg-white dark:bg-slate-800 text-sm text-right focus:outline-none focus:border-brand-500"
                      />
                      <span className="text-xs text-slate-400 shrink-0">so'm</span>

                      {fields.length > 1 && (
                        <button type="button" onClick={() => remove(idx)}
                          className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-red-400 transition shrink-0">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Add payment */}
              {fields.length < 3 && (
                <button
                  type="button"
                  onClick={() => append({ method: "card", amount: remaining > 0 ? remaining.toFixed(2) : "0" })}
                  className="mt-2 flex items-center gap-1.5 text-xs text-brand-500 hover:text-brand-600 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                  To'lov usuli qo'shish
                </button>
              )}
            </div>

            {/* Change / remaining */}
            {change > 0 && (
              <div className="flex items-center gap-2 p-3 bg-emerald-50 dark:bg-emerald-950/30
                rounded-xl border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span className="text-sm text-emerald-700 dark:text-emerald-400">
                  Qaytim: <strong>{formatCurrency(change)}</strong>
                </span>
              </div>
            )}
            {remaining > 0.01 && (
              <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-950/30
                rounded-xl border border-amber-200 dark:border-amber-800">
                <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />
                <div className="flex-1">
                  <span className="text-sm text-amber-700 dark:text-amber-400">
                    Qolgan summa: <strong>{formatCurrency(remaining)}</strong>
                  </span>
                  <p className="text-xs text-amber-600 dark:text-amber-500 mt-0.5">
                    {payments.some((p: any) => p.method === "debt")
                      ? "Nasiya sifatida saqlanadi"
                      : "To'liq to'lash uchun nasiya to'lov usulini qo'shing yoki summasini to'ldiring"
                    }
                  </p>
                </div>
              </div>
            )}

            {/* Note */}
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5 block">
                Izoh (ixtiyoriy)
              </label>
              <input
                {...register("note")}
                placeholder="Sotuv haqida izoh..."
                className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700
                  bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex gap-3">
            <button type="button" onClick={onClose}
              className="flex-1 h-11 rounded-xl border border-slate-200 dark:border-slate-700
                text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50
                dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={loading || (remaining > 0.01 && payments.every(p => p.method !== "debt"))}
              className="flex-2 flex-1 h-11 rounded-xl bg-brand-600 hover:bg-brand-500
                text-white text-sm font-semibold flex items-center justify-center gap-2
                transition disabled:opacity-60 disabled:cursor-not-allowed
                shadow-lg shadow-brand-600/25"
            >
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Saqlanmoqda...</>
                : <><CheckCircle2 className="w-4 h-4" /> Sotuvni yakunlash</>
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
