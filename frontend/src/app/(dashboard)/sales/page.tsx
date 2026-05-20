"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  Search, Receipt, TrendingUp, Banknote,
  CreditCard, Wallet, CalendarDays,
} from "lucide-react";
import { saleService } from "@/services/sale.service";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import { SaleTable }     from "@/components/sales/SaleTable";
import { SaleDetailDrawer } from "@/components/sales/SaleDetailDrawer";
import type { Sale } from "@/types";

export default function SalesPage() {
  const qc = useQueryClient();
  const [search,  setSearch]  = useState("");
  const [page,    setPage]    = useState(1);
  const [detail,  setDetail]  = useState<Sale | null>(null);
  const [dateFrom,setDateFrom]= useState("");
  const [dateTo,  setDateTo]  = useState("");
  const [status,  setStatus]  = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["sales", search, page, dateFrom, dateTo, status],
    queryFn:  () => saleService.getAll({
      search:    search    || undefined,
      date_from: dateFrom  || undefined,
      date_to:   dateTo    || undefined,
      status:    status    || undefined,
      page,
      page_size: 25,
    }),
  });

  const { data: summary } = useQuery({
    queryKey: ["sales-daily-summary"] as const,
    queryFn:  () => saleService.getDailySummary(),
    refetchInterval: 60_000 as number,
  });

  const returnMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      saleService.returnSale(id, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sales"] });
      toast.success("Sotuv qaytarildi");
      setDetail(null);
    },
    onError: (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  return (
    <div className="space-y-5">

      {/* Daily summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Receipt,     label: "Bugungi sotuvlar",  value: String((summary as any)?.total_sales ?? 0),          color: "blue"  },
          { icon: TrendingUp,  label: "Bugungi tushum",    value: formatCurrency((summary as any)?.total_revenue ?? 0), color: "green" },
          { icon: Banknote,    label: "Naqd",              value: formatCurrency((summary as any)?.total_cash ?? 0), color: "emerald"},
          { icon: Wallet,      label: "Nasiya",            value: formatCurrency((summary as any)?.total_debt ?? 0), color: "amber" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              color === "blue"    ? "bg-blue-50 dark:bg-blue-950/30 text-blue-600" :
              color === "green"   ? "bg-green-50 dark:bg-green-950/30 text-green-600" :
              color === "emerald" ? "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600" :
                                    "bg-amber-50 dark:bg-amber-950/30 text-amber-600"
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
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Chek raqami yoki kassir..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>

        {/* Date range */}
        <div className="flex items-center gap-2">
          <CalendarDays className="w-4 h-4 text-slate-400 shrink-0" />
          <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
            className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition w-36" />
          <span className="text-slate-400 text-sm">—</span>
          <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
            className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition w-36" />
        </div>

        {/* Status filter */}
        <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
          {[
            { val: "",           label: "Barchasi"  },
            { val: "completed",  label: "Yakunlangan"},
            { val: "returned",   label: "Qaytarilgan"},
          ].map(({ val, label }) => (
            <button key={val} onClick={() => { setStatus(val); setPage(1); }}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition",
                status === val
                  ? "bg-brand-600 text-white"
                  : "text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
              )}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <SaleTable
        sales={data?.results ?? []}
        isLoading={isLoading}
        total={data?.count ?? 0}
        page={page}
        totalPages={data?.total_pages ?? 1}
        onPageChange={setPage}
        onView={(s) => setDetail(s)}
      />

      {/* Detail drawer */}
      {detail && (
        <SaleDetailDrawer
          sale={detail}
          onClose={() => setDetail(null)}
          onReturn={(id, reason) => returnMutation.mutate({ id, reason })}
          isReturning={returnMutation.isPending}
        />
      )}
    </div>
  );
}
