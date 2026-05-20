"use client";
import { useState } from "react";
import {
  PackageCheck, Banknote, XCircle,
  ChevronLeft, ChevronRight, Loader2,
  ShoppingBag, AlertTriangle, Clock,
} from "lucide-react";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import type { Purchase, PurchaseStatus } from "@/types";

const STATUS_CONFIG: Record<PurchaseStatus, { label: string; cls: string }> = {
  draft:     { label: "Qoralama",        cls: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400" },
  received:  { label: "Qabul qilindi",   cls: "bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400" },
  partial:   { label: "Qisman to'landi", cls: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400" },
  paid:      { label: "To'landi",        cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400" },
  cancelled: { label: "Bekor qilindi",   cls: "bg-red-100 text-red-600 dark:bg-red-950/40 dark:text-red-400" },
};

interface Props {
  purchases:    Purchase[];
  isLoading:    boolean;
  total:        number;
  page:         number;
  totalPages:   number;
  onPageChange: (p: number) => void;
  onReceive:    (p: Purchase) => void;
  onPay:        (p: Purchase) => void;
  onCancel:     (p: Purchase) => void;
}

export function PurchaseTable({
  purchases, isLoading, total, page, totalPages,
  onPageChange, onReceive, onPay, onCancel,
}: Props) {
  const [confirmCancel, setConfirmCancel] = useState<number | null>(null);

  const handleCancel = (p: Purchase) => {
    if (confirmCancel === p.id) { onCancel(p); setConfirmCancel(null); }
    else setConfirmCancel(p.id);
  };

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
              {["Faktura", "Kompaniya", "Holat", "Jami summa", "Qarz", "To'lov muddati", "Sana", ""].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {purchases.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center">
                  <ShoppingBag className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-slate-400 text-sm">Xarid topilmadi</p>
                </td>
              </tr>
            ) : purchases.map((p) => {
              const status = STATUS_CONFIG[p.status] ?? STATUS_CONFIG.draft;
              const hasDebt = parseFloat(p.debt_amount) > 0;

              return (
                <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors group">

                  {/* Invoice */}
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs font-medium text-slate-700 dark:text-slate-200">
                      {p.invoice_no}
                    </span>
                  </td>

                  {/* Company */}
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-slate-800 dark:text-white text-sm">{p.company_name}</p>
                      {p.branch_name && (
                        <p className="text-xs text-slate-400">{p.branch_name}</p>
                      )}
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <span className={cn("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium", status.cls)}>
                      {status.label}
                    </span>
                  </td>

                  {/* Total */}
                  <td className="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">
                    {formatCurrency(p.total_amount)}
                  </td>

                  {/* Debt */}
                  <td className="px-4 py-3">
                    {hasDebt ? (
                      <span className="font-mono text-xs font-semibold text-red-500">
                        {formatCurrency(p.debt_amount)}
                      </span>
                    ) : (
                      <span className="text-xs text-emerald-500 font-medium">To'liq</span>
                    )}
                  </td>

                  {/* Due date */}
                  <td className="px-4 py-3">
                    {p.due_date ? (
                      <span className={cn(
                        "inline-flex items-center gap-1 text-xs font-medium",
                        p.is_overdue ? "text-red-500" : "text-slate-500"
                      )}>
                        {p.is_overdue && <AlertTriangle className="w-3 h-3" />}
                        {formatDate(p.due_date)}
                      </span>
                    ) : (
                      <span className="text-slate-300 dark:text-slate-600 text-xs">—</span>
                    )}
                  </td>

                  {/* Created */}
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {formatDate(p.created_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">

                      {/* Receive — only draft */}
                      {p.status === "draft" && (
                        <ActionBtn
                          onClick={() => onReceive(p)}
                          icon={PackageCheck}
                          label="Qabul qilish"
                          colorCls="hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-950/30"
                        />
                      )}

                      {/* Pay — received or partial */}
                      {(p.status === "received" || p.status === "partial") && hasDebt && (
                        <ActionBtn
                          onClick={() => onPay(p)}
                          icon={Banknote}
                          label="To'lash"
                          colorCls="hover:text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                        />
                      )}

                      {/* Cancel — only draft */}
                      {p.status === "draft" && (
                        <ActionBtn
                          onClick={() => handleCancel(p)}
                          icon={XCircle}
                          label={confirmCancel === p.id ? "Tasdiqla" : "Bekor qilish"}
                          colorCls={
                            confirmCancel === p.id
                              ? "bg-red-500 text-white hover:bg-red-600"
                              : "hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
                          }
                        />
                      )}
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
          <p className="text-xs text-slate-500">Jami {total} ta xarid</p>
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

function ActionBtn({ onClick, icon: Icon, label, colorCls }: {
  onClick:  () => void;
  icon:     React.ElementType;
  label:    string;
  colorCls: string;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className={cn(
        "w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 transition",
        colorCls
      )}
    >
      <Icon className="w-3.5 h-3.5" />
    </button>
  );
}
