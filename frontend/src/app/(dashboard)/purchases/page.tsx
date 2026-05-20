"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { Plus, Search, Filter, ShoppingBag, AlertTriangle, Clock, Banknote, TrendingDown } from "lucide-react";
import { purchaseService } from "@/services/purchase.service";
import { formatCurrency } from "@/lib/utils";
import { PurchaseTable }  from "@/components/purchases/PurchaseTable";
import { PurchaseModal }  from "@/components/purchases/PurchaseModal";
import { PayDebtModal }   from "@/components/purchases/PayDebtModal";
import { PurchaseFilter } from "@/components/purchases/PurchaseFilter";
import type { Purchase }  from "@/types";

export default function PurchasesPage() {
  const qc = useQueryClient();
  const [search,     setSearch]     = useState("");
  const [filterOpen, setFilterOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [payTarget,  setPayTarget]  = useState<Purchase | null>(null);
  const [filters,    setFilters]    = useState<Record<string, string>>({});
  const [page,       setPage]       = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["purchases", search, filters, page],
    queryFn:  () => purchaseService.getAll({ page, page_size: 20, search: search || undefined, ...filters }),
  });

  const { data: debtsData } = useQuery({
    queryKey: ["purchases-debts"],
    queryFn:  purchaseService.getDebts,
  });

  const receiveMutation = useMutation({
    mutationFn: (id: number) => purchaseService.receive(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["purchases"] }); toast.success("Xarid qabul qilindi — omborga tushirildi"); },
    onError:   (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => purchaseService.cancel(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["purchases"] }); toast.success("Xarid bekor qilindi"); },
    onError:   (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  const totalDebt    = debtsData?.data?.total_debt    ?? "0";
  const overdueCount = debtsData?.data?.overdue_count ?? 0;

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {([
          { icon: ShoppingBag, color: "blue",  label: "Jami xaridlar",    value: String(data?.count ?? 0) },
          { icon: Banknote,    color: "amber", label: "Umumiy qarz",       value: formatCurrency(totalDebt) },
          { icon: Clock,       color: "red",   label: "Muddati o'tgan",    value: `${overdueCount} ta` },
          { icon: TrendingDown,color: "green", label: "Draft holatida",    value: "—" },
        ] as const).map(({ icon: Icon, color, label, value }) => (
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
            placeholder="Kompaniya yoki faktura raqami..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>
        <button onClick={() => setFilterOpen(true)}
          className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
          <Filter className="w-4 h-4" />
          Filtr
          {Object.keys(filters).length > 0 && (
            <span className="w-4 h-4 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center">{Object.keys(filters).length}</span>
          )}
        </button>
        <button onClick={() => setCreateOpen(true)}
          className="h-9 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-2 text-sm font-medium transition shadow-sm shadow-brand-600/20">
          <Plus className="w-4 h-4" /> Yangi xarid
        </button>
      </div>

      {/* Overdue alert */}
      {overdueCount > 0 && (
        <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-950/30 rounded-xl border border-red-200 dark:border-red-800">
          <AlertTriangle className="w-4 h-4 text-red-500 shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-400">
            <strong>{overdueCount} ta xarid</strong>ning to'lov muddati o'tib ketdi.
          </p>
        </div>
      )}

      {/* Table */}
      <PurchaseTable
        purchases={data?.results ?? []} isLoading={isLoading}
        total={data?.count ?? 0} page={page} totalPages={data?.total_pages ?? 1}
        onPageChange={setPage}
        onReceive={(p) => receiveMutation.mutate(p.id)}
        onPay={(p) => setPayTarget(p)}
        onCancel={(p) => cancelMutation.mutate(p.id)}
      />

      {filterOpen && <PurchaseFilter filters={filters} onApply={(f) => { setFilters(f); setFilterOpen(false); setPage(1); }} onClose={() => setFilterOpen(false)} />}
      {createOpen && <PurchaseModal  onClose={() => setCreateOpen(false)} onSaved={() => { qc.invalidateQueries({ queryKey: ["purchases"] }); setCreateOpen(false); }} />}
      {payTarget  && <PayDebtModal   purchase={payTarget} onClose={() => setPayTarget(null)} onPaid={() => { qc.invalidateQueries({ queryKey: ["purchases", "purchases-debts"] }); setPayTarget(null); }} />}
    </div>
  );
}
