"use client";
import { useRef } from "react";
import {
  X, Printer, CheckCircle2, Banknote, CreditCard, Wallet,
  Store, Calendar, User,
} from "lucide-react";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import type { Sale } from "@/types";

const METHOD_ICONS: Record<string, any> = {
  cash: Banknote, card: CreditCard, debt: Wallet,
};
const METHOD_LABELS: Record<string, string> = {
  cash: "Naqd", card: "Karta", debt: "Nasiya",
};

interface Props {
  sale:    Sale;
  onClose: () => void;
}

export function ReceiptModal({ sale, onClose }: Props) {
  const printRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    if (!printRef.current) return;
    const win = window.open("", "_blank");
    if (!win) return;
    win.document.write(`
      <html><head><title>Chek #${sale.invoice_no}</title>
      <style>
        body { font-family: monospace; font-size: 12px; width: 300px; margin: 0 auto; padding: 10px; }
        .center { text-align: center; }
        .divider { border-top: 1px dashed #000; margin: 6px 0; }
        .row { display: flex; justify-content: space-between; }
        .bold { font-weight: bold; }
        .large { font-size: 16px; font-weight: bold; }
      </style></head><body>
      ${printRef.current.innerHTML}
      </body></html>
    `);
    win.document.close();
    win.print();
    win.close();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 text-emerald-600">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-semibold text-slate-800 dark:text-white">Sotuv yakunlandi</span>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400
              hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Receipt */}
        <div className="p-6">
          <div ref={printRef}
            className="bg-slate-50 dark:bg-slate-800 rounded-xl p-5 font-mono text-xs space-y-3">

            {/* Store header */}
            <div className="text-center space-y-0.5">
              <div className="flex items-center justify-center gap-1.5 mb-1">
                <Store className="w-4 h-4" />
                <span className="font-bold text-sm">Mini Market</span>
              </div>
              <p className="text-slate-500 dark:text-slate-400">POS tizimi</p>
              <div className="border-t border-dashed border-slate-300 dark:border-slate-600 my-2" />
            </div>

            {/* Invoice info */}
            <div className="space-y-1 text-slate-600 dark:text-slate-300">
              <div className="flex justify-between">
                <span>Chek #</span>
                <span className="font-bold">{sale.invoice_no}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Sana
                </span>
                <span>{formatDateTime(sale.created_at)}</span>
              </div>
              {sale.cashier_name && (
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    Kassir
                  </span>
                  <span>{sale.cashier_name}</span>
                </div>
              )}
            </div>

            <div className="border-t border-dashed border-slate-300 dark:border-slate-600" />

            {/* Amounts */}
            <div className="space-y-1 text-slate-600 dark:text-slate-300">
              <div className="flex justify-between">
                <span>Jami summa</span>
                <span>{formatCurrency(sale.total_amount)}</span>
              </div>
              {parseFloat(sale.discount_amount) > 0 && (
                <div className="flex justify-between text-emerald-600">
                  <span>Chegirma ({sale.discount_pct}%)</span>
                  <span>−{formatCurrency(sale.discount_amount)}</span>
                </div>
              )}
              <div className="flex justify-between font-bold text-slate-800 dark:text-white text-sm mt-1">
                <span>To'lanadigan</span>
                <span>{formatCurrency(sale.net_amount)}</span>
              </div>
            </div>

            <div className="border-t border-dashed border-slate-300 dark:border-slate-600" />

            {/* Payments */}
            <div className="space-y-1 text-slate-600 dark:text-slate-300">
              {(sale.payment_methods ?? []).map((method, i) => {
                const Icon = METHOD_ICONS[method] || Banknote;
                return (
                  <div key={i} className="flex justify-between items-center">
                    <span className="flex items-center gap-1">
                      <Icon className="w-3 h-3" />
                      {METHOD_LABELS[method] || method}
                    </span>
                  </div>
                );
              })}
              {parseFloat(sale.debt_amount) > 0 && (
                <div className="flex justify-between text-amber-600">
                  <span>Nasiya qoldig'i</span>
                  <span>{formatCurrency(sale.debt_amount)}</span>
                </div>
              )}
            </div>

            <div className="border-t border-dashed border-slate-300 dark:border-slate-600" />

            <p className="text-center text-slate-400 dark:text-slate-500">
              Xarid uchun rahmat! 🛍️
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 pb-6 flex gap-3">
          <button
            onClick={handlePrint}
            className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700
              flex items-center justify-center gap-2 text-sm font-medium text-slate-600
              dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            <Printer className="w-4 h-4" />
            Chop etish
          </button>
          <button
            onClick={onClose}
            className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500
              text-white text-sm font-semibold transition shadow-lg shadow-brand-600/25"
          >
            Yangi sotuv
          </button>
        </div>
      </div>
    </div>
  );
}
