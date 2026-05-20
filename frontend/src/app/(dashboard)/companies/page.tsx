"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { Plus, Search, Building2, GitBranch, Wallet, Pencil, Trash2, ChevronRight, Loader2 } from "lucide-react";
import { companyService } from "@/services/company.service";
import { formatCurrency } from "@/lib/utils";
import { CompanyModal }  from "@/components/companies/CompanyModal";
import { BranchesDrawer } from "@/components/companies/BranchesDrawer";
import type { Company } from "@/types";

export default function CompaniesPage() {
  const qc = useQueryClient();
  const [search,     setSearch]     = useState("");
  const [page,       setPage]       = useState(1);
  const [modal,      setModal]      = useState<Company | null | "new">(null);
  const [branches,   setBranches]   = useState<Company | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["companies", search, page],
    queryFn:  () => companyService.getAll({ search: search || undefined, page, page_size: 20 }),
  });

  const deleteMutation = useMutation({
    mutationFn: companyService.delete,
    onSuccess:  () => { qc.invalidateQueries({ queryKey: ["companies"] }); toast.success("Kompaniya o'chirildi"); },
    onError:    (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: Building2, label: "Kompaniyalar", value: data?.count ?? 0,   color: "blue"  },
          { icon: GitBranch, label: "Filiallar",     value: "—",                color: "green" },
          { icon: Wallet,    label: "Umumiy qarz",   value: "—",                color: "amber" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
              color === "blue"  ? "bg-blue-50 dark:bg-blue-950/30 text-blue-600" :
              color === "green" ? "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600" :
                                  "bg-amber-50 dark:bg-amber-950/30 text-amber-600"
            }`}><Icon className="w-4 h-4" /></div>
            <div><p className="text-xs text-slate-500">{label}</p><p className="font-bold text-slate-800 dark:text-white">{value}</p></div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Kompaniya nomi yoki INN..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>
        <button onClick={() => setModal("new")}
          className="h-9 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-2 text-sm font-medium transition shadow-sm shadow-brand-600/20">
          <Plus className="w-4 h-4" /> Qo'shish
        </button>
      </div>

      {/* Cards grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="w-6 h-6 text-brand-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.results.length === 0 && (
            <div className="col-span-full flex flex-col items-center justify-center h-48 text-slate-400">
              <Building2 className="w-8 h-8 mb-2 opacity-40" />
              <p className="text-sm">Kompaniya topilmadi</p>
            </div>
          )}
          {data?.results.map((company) => (
            <CompanyCard key={company.id} company={company}
              onEdit={() => setModal(company)}
              onDelete={() => deleteMutation.mutate(company.id)}
              onBranches={() => setBranches(company)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {(data?.total_pages ?? 1) > 1 && (
        <div className="flex justify-center gap-2">
          <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}
            className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition">
            ← Oldingi
          </button>
          <span className="h-8 px-3 rounded-lg bg-brand-600 text-white text-sm flex items-center">{page}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= (data?.total_pages ?? 1)}
            className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition">
            Keyingi →
          </button>
        </div>
      )}

      {modal !== null && (
        <CompanyModal
          company={modal === "new" ? null : modal}
          onClose={() => setModal(null)}
          onSaved={() => { qc.invalidateQueries({ queryKey: ["companies"] }); setModal(null); }}
        />
      )}
      {branches !== null && (
        <BranchesDrawer
          company={branches}
          onClose={() => setBranches(null)}
        />
      )}
    </div>
  );
}

function CompanyCard({ company, onEdit, onDelete, onBranches }: {
  company:   Company;
  onEdit:    () => void;
  onDelete:  () => void;
  onBranches:() => void;
}) {
  const [confirmDel, setConfirmDel] = useState(false);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 hover:shadow-md hover:shadow-slate-200/60 dark:hover:shadow-black/20 transition-shadow group">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-brand-600/10 flex items-center justify-center shrink-0">
            <Building2 className="w-5 h-5 text-brand-600" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-slate-800 dark:text-white text-sm truncate">{company.name}</h3>
            {company.inn && <p className="text-xs text-slate-400 font-mono">INN: {company.inn}</p>}
          </div>
        </div>
        {/* Actions */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
          <button onClick={onEdit}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition">
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => confirmDel ? onDelete() : setConfirmDel(true)}
            className={`w-7 h-7 rounded-lg flex items-center justify-center transition ${
              confirmDel ? "bg-red-500 text-white" : "text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
            }`}
            title={confirmDel ? "Yana bosing" : "O'chirish"}>
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="space-y-1.5 text-xs text-slate-500 mb-4">
        {company.phone   && <p className="flex items-center gap-1.5"><span className="w-3.5">📞</span>{company.phone}</p>}
        {company.address && <p className="flex items-center gap-1.5 truncate"><span className="w-3.5">📍</span>{company.address}</p>}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
        <button onClick={onBranches}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-brand-600 transition">
          <GitBranch className="w-3.5 h-3.5" />
          {company.branch_count ?? 0} ta filial
          <ChevronRight className="w-3 h-3" />
        </button>
        <span className="text-xs font-medium text-slate-400">
          {new Date(company.created_at).toLocaleDateString("uz-UZ")}
        </span>
      </div>
    </div>
  );
}
