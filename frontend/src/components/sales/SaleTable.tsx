"use client";
import {
  Eye, Receipt, Loader2,
  ChevronLeft, ChevronRight,
  Banknote, CreditCard, Wallet,
} from "lucide-react";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import type { Sale, PaymentMethod, SaleStatus } from "@/types";

const STATUS_CONFIG: Record<SaleStatus, { label: string; cls: string }> = {
  completed: { label: "Yakunlangan",  cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400" },
  returned:  { label: "Qaytarilgan",  cls: "bg-red-100 text-red-600 dark:bg-red-950/40 dark:text-red-400"                 },
  partial:   { label: "Qisman",       cls: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400"         },
};

const METHOD_ICONS: Record<PaymentMethod, React.ElementType> = {
  cash: Banknote, card: CreditCard, debt: Wallet,
};
const METHOD_LABELS: Record<PaymentMethod, string> = {
  cash: "Naqd", card: "Karta", debt: "Nasiya",
};

interface Props {
  sales:        Sale[];
  isLoading:    boolean;
  total:        number;
  page:         number;
  totalPages:   number;
  onPageChange: (p: number) => void;
  onView:       (s: Sale) => void;
}

export function SaleTable({
  sales, isLoading, total, page, totalPages, onPageChange, onView,
}: Props) {

  if (isLoading) return (
    <div className="flex items-center justify-center h-48 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
      <Loader2 className="w-6 h-6 text-brand-500 animate-spin" />
    </div>
  );

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              {["Chek #", "Holat", "To'lov usuli", "Jami", "Chegirma", "Nasiya", "Kassir", "Sana", ""].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {sales.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-12 text-center">
                  <Receipt className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-slate-400 text-sm">Sotuv topilmadi</p>
                </td>
              </tr>
            ) : sales.map((sale) => {
              const status = STATUS_CONFIG[sale.status] ?? STATUS_CONFIG.completed;

              return (
                <tr key={sale.id}
                  onClick={() => onView(sale)}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors cursor-pointer group">

                  {/* Invoice */}
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs font-semibold text-brand-600 dark:text-brand-400">
                      {sale.invoice_no}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <span className={cn("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium", status.cls)}>
                      {status.label}
                    </span>
                  </td>

                  {/* Payment methods */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {sale.payment_methods.map((method) => {
                        const Icon = METHOD_ICONS[method] ?? Banknote;
                        return (
                          <div key={method}
                            title={METHOD_LABELS[method]}
                            className="w-6 h-6 rounded-md bg-slate-100 dark:bg-slate-700 flex items-center justify-center"
                          >
                            <Icon className="w-3.5 h-3.5 text-slate-500" />
                          </div>
                        );
                      })}
                    </div>
                  </td>

                  {/* Net amount */}
                  <td className="px-4 py-3">
                    <span className="font-semibold text-slate-800 dark:text-white font-mono text-xs">
                      {formatCurrency(sale.net_amount)}
                    </span>
                  </td>

                  {/* Discount */}
                  <td className="px-4 py-3 text-xs text-slate-500 font-mono">
                    {parseFloat(sale.discount_amount) > 0
                      ? <span className="text-emerald-600">−{formatCurrency(sale.discount_amount)}</span>
                      : <span className="text-slate-300 dark:text-slate-600">—</span>
                    }
                  </td>

                  {/* Debt */}
                  <td className="px-4 py-3 text-xs font-mono">
                    {parseFloat(sale.debt_amount) > 0
                      ? <span className="font-semibold text-amber-600">{formatCurrency(sale.debt_amount)}</span>
                      : <span className="text-slate-300 dark:text-slate-600">—</span>
                    }
                  </td>

                  {/* Cashier */}
                  <td className="px-4 py-3 text-xs text-slate-500 max-w-[120px] truncate">
                    {sale.cashier_name ?? "—"}
                  </td>

                  {/* Date */}
                  <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                    {formatDateTime(sale.created_at)}
                  </td>

                  {/* View */}
                  <td className="px-4 py-3">
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400
                      opacity-0 group-hover:opacity-100 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition">
                      <Eye className="w-3.5 h-3.5" />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-500">Jami {total} ta sotuv</p>
          <div className="flex items-center gap-1">
            <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
              className="w-7 h-7 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 text-xs text-slate-600 dark:text-slate-300">{page} / {totalPages}</span>
            <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
              className="w-7 h-7 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
