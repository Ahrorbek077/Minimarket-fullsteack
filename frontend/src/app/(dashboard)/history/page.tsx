"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Search, History, LogIn, LogOut, ShoppingCart,
  Package, Building2, Warehouse, Settings, AlertTriangle,
} from "lucide-react";
import { historyService } from "@/services/history.service";
import { LogItem, MODEL_LABELS } from "@/components/history/LogItem";
import { formatDateTime, cn } from "@/lib/utils";
import type { AuditLog } from "@/services/history.service";



export default function HistoryPage() {
  const [search,  setSearch]  = useState("");
  const [action,  setAction]  = useState("");
  const [model,   setModel]   = useState("");
  const [page,    setPage]    = useState(1);
  const [expanded,setExpanded]= useState<number | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs", search, action, model, page],
    queryFn:  () => historyService.getLogs({
      search:     search || undefined,
      action:     action || undefined,
      model_name: model  || undefined,
      page,
      page_size: 30,
    }),
  });

  return (
    <div className="space-y-5">

      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Foydalanuvchi email yoki ob'ekt..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>

        {/* Model filter */}
        <select value={model} onChange={(e) => { setModel(e.target.value); setPage(1); }}
          className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition">
          <option value="">Barcha model</option>
          {Object.entries(MODEL_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>

        {/* Action filter */}
        <select value={action} onChange={(e) => { setAction(e.target.value); setPage(1); }}
          className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition">
          <option value="">Barcha amal</option>
          <option value="login">Kirish</option>
          <option value="logout">Chiqish</option>
          <option value="sale_checkout">Sotuv</option>
          <option value="create">Yaratish</option>
          <option value="update">Yangilash</option>
          <option value="delete">O'chirish</option>
        </select>
      </div>

      {/* Logs */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : data?.results.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <History className="w-8 h-8 mb-2 opacity-30" />
            <p className="text-sm">Tarix topilmadi</p>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100 dark:divide-slate-800">
            {data?.results.map((log) => (
              <LogItem
                key={log.id}
                log={log}
                isExpanded={expanded === log.id}
                onToggle={() => setExpanded(expanded === log.id ? null : log.id)}
              />
            ))}
          </ul>
        )}

        {/* Pagination */}
        {(data?.total_pages ?? 1) > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs text-slate-500">Jami {data?.count} ta yozuv</p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}
                className="h-7 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
                ← Oldingi
              </button>
              <span className="px-3 text-xs text-slate-500">{page} / {data?.total_pages}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={page >= (data?.total_pages ?? 1)}
                className="h-7 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition">
                Keyingi →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

