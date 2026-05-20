"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, ArrowUp, ArrowDown, RotateCcw, History, Loader2 } from "lucide-react";
import { inventoryService } from "@/services/inventory.service";
import { formatDateTime, cn } from "@/lib/utils";
import type { Stock } from "@/services/inventory.service";

interface Props {
  stock:   Stock;
  onClose: () => void;
}

const TYPE_CONFIG = {
  in:         { label: "Kirim",       Icon: ArrowUp,    cls: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30" },
  out:        { label: "Chiqim",      Icon: ArrowDown,  cls: "text-red-500 bg-red-50 dark:bg-red-950/30"            },
  adjustment: { label: "To'g'irlash", Icon: RotateCcw,  cls: "text-blue-500 bg-blue-50 dark:bg-blue-950/30"        },
};

export function MovementsDrawer({ stock, onClose }: Props) {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["movements", stock.product_id, page],
    queryFn:  () => inventoryService.getMovements({
      product_id: stock.product_id,
      page,
      page_size:  20,
    }),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-brand-500" />
              <h2 className="font-semibold text-slate-800 dark:text-white">Harakat tarixi</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 truncate max-w-[280px]">{stock.product_name}</p>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
            </div>
          ) : data?.results.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-slate-400">
              <History className="w-7 h-7 mb-2 opacity-30" />
              <p className="text-sm">Harakat tarixi yo'q</p>
            </div>
          ) : (
            data?.results.map((mv) => {
              const cfg = TYPE_CONFIG[mv.type] ?? TYPE_CONFIG.adjustment;
              const qty = parseFloat(mv.quantity);
              return (
                <div key={mv.id}
                  className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700/60 transition">
                  <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center shrink-0", cfg.cls)}>
                    <cfg.Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-slate-700 dark:text-slate-200">{cfg.label}</span>
                      <span className={cn(
                        "text-sm font-bold",
                        mv.type === "in" ? "text-emerald-600" :
                        mv.type === "out" ? "text-red-500" : "text-blue-500"
                      )}>
                        {mv.type === "out" ? "−" : "+"}{qty} {stock.unit_short}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 truncate mt-0.5">{mv.reason || "—"}</p>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-slate-400">{mv.created_by ?? "Tizim"}</span>
                      <span className="text-xs text-slate-400">{formatDateTime(mv.created_at)}</span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Pagination */}
        {(data?.total_pages ?? 1) > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800 shrink-0">
            <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}
              className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
              ← Oldingi
            </button>
            <span className="text-xs text-slate-500">{page} / {data?.total_pages}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= (data?.total_pages ?? 1)}
              className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
              Keyingi →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
