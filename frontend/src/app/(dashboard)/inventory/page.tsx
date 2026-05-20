"use client";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  Search, Filter, Warehouse, AlertTriangle,
  TrendingDown, DollarSign, ArrowUpDown,
} from "lucide-react";
import { inventoryService } from "@/services/inventory.service";
import { formatCurrency, cn } from "@/lib/utils";
import { AdjustModal }   from "@/components/inventory/AdjustModal";
import { MovementsDrawer } from "@/components/inventory/MovementsDrawer";
import type { Stock } from "@/services/inventory.service";

export default function InventoryPage() {
  const qc = useQueryClient();
  const [search,    setSearch]    = useState("");
  const [filter,    setFilter]    = useState<"all" | "low" | "out">("all");
  const [page,      setPage]      = useState(1);
  const [adjusting, setAdjusting] = useState<Stock | null>(null);
  const [movements, setMovements] = useState<Stock | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["stocks", search, filter, page],
    queryFn:  () => inventoryService.getStocks({
      search:    search || undefined,
      low_stock: filter === "low" ? "true" : undefined,
      out_stock: filter === "out" ? "true" : undefined,
      page,
      page_size: 25,
    }),
  });

  // Summary from data
  const lowCount  = data?.results.filter(s => s.is_low && parseFloat(s.quantity) > 0).length ?? 0;
  const outCount  = data?.results.filter(s => parseFloat(s.quantity) <= 0).length ?? 0;
  const totalCost = data?.results.reduce((s, r) => s + parseFloat(r.cost_value || "0"), 0) ?? 0;

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Warehouse,     label: "Jami pozitsiya",  value: String(data?.count ?? 0),   color: "blue"  },
          { icon: AlertTriangle, label: "Kam qoldiq",       value: `${lowCount} ta`,            color: "amber" },
          { icon: TrendingDown,  label: "Tugagan",          value: `${outCount} ta`,            color: "red"   },
          { icon: DollarSign,    label: "Ombor qiymati",    value: formatCurrency(totalCost),   color: "green" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              color === "blue"  ? "bg-blue-50 dark:bg-blue-950/30 text-blue-600" :
              color === "amber" ? "bg-amber-50 dark:bg-amber-950/30 text-amber-600" :
              color === "red"   ? "bg-red-50 dark:bg-red-950/30 text-red-500" :
                                  "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600"
            }`}><Icon className="w-4 h-4" /></div>
            <div className="min-w-0">
              <p className="text-xs text-slate-500 truncate">{label}</p>
              <p className="font-bold text-slate-800 dark:text-white truncate">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Mahsulot nomi yoki barcode..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>

        {/* Filter tabs */}
        <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
          {(["all", "low", "out"] as const).map((f) => (
            <button key={f} onClick={() => { setFilter(f); setPage(1); }}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition",
                filter === f
                  ? "bg-brand-600 text-white"
                  : "text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
              )}>
              {f === "all" ? "Barchasi" : f === "low" ? "Kam qoldiq" : "Tugagan"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                {["Mahsulot", "Kategoriya", "Qoldiq", "Min", "Tan narxi", "Sotish narxi", "Qiymati", ""].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {isLoading ? (
                <tr><td colSpan={8} className="px-4 py-12 text-center">
                  <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
                </td></tr>
              ) : data?.results.length === 0 ? (
                <tr><td colSpan={8} className="px-4 py-12 text-center">
                  <Warehouse className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-slate-400 text-sm">Mahsulot topilmadi</p>
                </td></tr>
              ) : data?.results.map((stock) => {
                const qty      = parseFloat(stock.quantity);
                const minStock = parseFloat(stock.min_stock);
                const isOut    = qty <= 0;
                const isLow    = !isOut && stock.is_low;

                return (
                  <tr key={stock.id}
                    className={cn(
                      "hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors group",
                      isOut ? "bg-red-50/30 dark:bg-red-950/10" : isLow ? "bg-amber-50/30 dark:bg-amber-950/10" : ""
                    )}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-800 dark:text-white text-sm">{stock.product_name}</p>
                      {stock.product_barcode && (
                        <p className="text-xs text-slate-400 font-mono">{stock.product_barcode}</p>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{stock.category_name ?? "—"}</td>

                    {/* Quantity */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className={cn(
                          "font-bold text-sm",
                          isOut ? "text-red-500" : isLow ? "text-amber-600" : "text-slate-800 dark:text-white"
                        )}>
                          {qty} {stock.unit_short}
                        </span>
                        {(isOut || isLow) && (
                          <AlertTriangle className={cn(
                            "w-3.5 h-3.5 shrink-0",
                            isOut ? "text-red-500" : "text-amber-500"
                          )} />
                        )}
                      </div>
                    </td>

                    <td className="px-4 py-3 text-xs text-slate-500">{minStock} {stock.unit_short}</td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-600 dark:text-slate-300">{formatCurrency(stock.cost_price)}</td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-600 dark:text-slate-300">{formatCurrency(stock.sell_price)}</td>
                    <td className="px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-200">{formatCurrency(stock.cost_value)}</td>

                    {/* Actions */}
                    <td className="px-4 py-3">
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setAdjusting(stock)}
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition"
                          title="Qoldiqni o'zgartirish">
                          <ArrowUpDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {(data?.total_pages ?? 1) > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs text-slate-500">Jami {data?.count} ta</p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}
                className="h-7 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">← Oldingi</button>
              <span className="px-3 text-xs text-slate-600 dark:text-slate-300">{page} / {data?.total_pages}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={page >= (data?.total_pages ?? 1)}
                className="h-7 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">Keyingi →</button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {adjusting !== null && (
        <AdjustModal
          stock={adjusting}
          onClose={() => setAdjusting(null)}
          onSaved={() => { qc.invalidateQueries({ queryKey: ["stocks"] }); setAdjusting(null); }}
        />
      )}
    </div>
  );
}
