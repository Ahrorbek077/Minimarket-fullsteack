"use client";
import { useState } from "react";
import {
  Pencil, Trash2, ChevronLeft, ChevronRight,
  Barcode, Package, Loader2, AlertTriangle,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Product } from "@/types";

interface Props {
  products:     Product[];
  isLoading:    boolean;
  total:        number;
  page:         number;
  totalPages:   number;
  onPageChange: (p: number) => void;
  onEdit:       (p: Product) => void;
  onDelete:     (id: number) => void;
}

export function ProductTable({
  products, isLoading, total, page, totalPages,
  onPageChange, onEdit, onDelete,
}: Props) {
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const handleDelete = (id: number) => {
    if (confirmId === id) { onDelete(id); setConfirmId(null); }
    else setConfirmId(id);
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
              {["Mahsulot", "Barcode", "Kategoriya", "Birlik", "Tan narxi", "Sotish narxi", "Foyda %", "Qoldiq", "Holat", ""].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {products.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-12 text-center">
                  <Package className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-slate-400 text-sm">Mahsulot topilmadi</p>
                </td>
              </tr>
            ) : products.map((p) => (
              <tr key={p.id}
                className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group">

                {/* Name + image */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center shrink-0 overflow-hidden">
                      {p.image
                        ? <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
                        : <Package className="w-4 h-4 text-slate-400" />
                      }
                    </div>
                    <span className="font-medium text-slate-800 dark:text-white max-w-[180px] truncate">
                      {p.name}
                    </span>
                  </div>
                </td>

                {/* Barcode */}
                <td className="px-4 py-3">
                  {p.barcode
                    ? <div className="flex items-center gap-1 text-slate-500 font-mono text-xs">
                        <Barcode className="w-3.5 h-3.5" />
                        {p.barcode}
                      </div>
                    : <span className="text-slate-300 dark:text-slate-600 text-xs">—</span>
                  }
                </td>

                <td className="px-4 py-3 text-slate-500 text-xs">{p.category_name ?? "—"}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{p.unit_short ?? "—"}</td>

                {/* Prices */}
                <td className="px-4 py-3 text-slate-600 dark:text-slate-300 font-mono text-xs">
                  {formatCurrency(p.cost_price)}
                </td>
                <td className="px-4 py-3 font-semibold text-slate-800 dark:text-white font-mono text-xs">
                  {formatCurrency(p.sell_price)}
                </td>

                {/* Profit */}
                <td className="px-4 py-3">
                  <span className={cn(
                    "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                    p.profit_margin >= 20 ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400"
                    : p.profit_margin >= 10 ? "bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400"
                    : "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400"
                  )}>
                    {p.profit_margin}%
                  </span>
                </td>

                {/* Stock */}
                <td className="px-4 py-3">
                  <span className={cn(
                    "text-sm font-medium",
                    p.stock_qty <= 0        ? "text-red-500"
                    : p.is_low_stock        ? "text-amber-500"
                    : "text-slate-700 dark:text-slate-300"
                  )}>
                    {p.stock_qty <= 0
                      ? <span className="flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" />Tugagan</span>
                      : <>{p.stock_qty} {p.unit_short}</>
                    }
                  </span>
                </td>

                {/* Active */}
                <td className="px-4 py-3">
                  <span className={cn(
                    "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                    p.is_active
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400"
                      : "bg-slate-100 text-slate-500 dark:bg-slate-800"
                  )}>
                    {p.is_active ? "Aktiv" : "Nofaol"}
                  </span>
                </td>

                {/* Actions */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => onEdit(p)}
                      className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400
                        hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition">
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => handleDelete(p.id)}
                      className={cn(
                        "w-7 h-7 rounded-lg flex items-center justify-center transition",
                        confirmId === p.id
                          ? "bg-red-500 text-white"
                          : "text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
                      )}
                      title={confirmId === p.id ? "Yana bosing — tasdiqlash" : "O'chirish"}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-500">Jami {total} ta mahsulot</p>
          <div className="flex items-center gap-1">
            <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
              className="w-7 h-7 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 text-xs text-slate-600 dark:text-slate-300">
              {page} / {totalPages}
            </span>
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
