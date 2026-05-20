"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { Plus, Search, Filter, Package, AlertTriangle, TrendingDown, BarChart2 } from "lucide-react";
import { productService } from "@/services/product.service";
import { ProductTable }  from "@/components/products/ProductTable";
import { ProductModal }  from "@/components/products/ProductModal";
import { ProductFilter } from "@/components/products/ProductFilter";
import type { Product }  from "@/types";

export default function ProductsPage() {
  const qc = useQueryClient();
  const [search,       setSearch]       = useState("");
  const [filterOpen,   setFilterOpen]   = useState(false);
  const [modalProduct, setModalProduct] = useState<Product | null | "new">(null);
  const [filters,      setFilters]      = useState<Record<string, any>>({});
  const [page,         setPage]         = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["products", search, filters, page],
    queryFn:  () => productService.getProducts({ search: search || undefined, page, page_size: 20, ...filters }),
  });

  const deleteMutation = useMutation({
    mutationFn: productService.deleteProduct,
    onSuccess:  () => { qc.invalidateQueries({ queryKey: ["products"] }); toast.success("Mahsulot o'chirildi"); },
    onError:    () => toast.error("Xato yuz berdi"),
  });

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Package,       label: "Jami",       value: data?.count ?? 0, c: "blue"  },
          { icon: AlertTriangle, label: "Kam qoldiq",  value: "—",              c: "amber" },
          { icon: TrendingDown,  label: "Tugagan",     value: "—",              c: "red"   },
          { icon: BarChart2,     label: "Kategoriya",  value: "—",              c: "green" },
        ].map(({ icon: Icon, label, value, c }) => (
          <div key={label} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0
              ${c==="blue"?"bg-blue-50 text-blue-600":c==="amber"?"bg-amber-50 text-amber-600":c==="red"?"bg-red-50 text-red-500":"bg-emerald-50 text-emerald-600"}`}>
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs text-slate-500">{label}</p>
              <p className="font-bold text-slate-800 dark:text-white">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Nomi yoki barcode..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>
        <button onClick={() => setFilterOpen(true)}
          className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
          <Filter className="w-4 h-4" />
          Filtr {Object.keys(filters).length > 0 && <span className="w-4 h-4 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center">{Object.keys(filters).length}</span>}
        </button>
        <button onClick={() => setModalProduct("new")}
          className="h-9 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-2 text-sm font-medium transition">
          <Plus className="w-4 h-4" /> Qo'shish
        </button>
      </div>

      {/* Table */}
      <ProductTable
        products={data?.results ?? []} isLoading={isLoading}
        total={data?.count ?? 0} page={page} totalPages={data?.total_pages ?? 1}
        onPageChange={setPage}
        onEdit={(p) => setModalProduct(p)}
        onDelete={(id) => deleteMutation.mutate(id)}
      />

      {/* Modals */}
      {filterOpen && <ProductFilter filters={filters} onApply={(f) => { setFilters(f); setFilterOpen(false); setPage(1); }} onClose={() => setFilterOpen(false)} />}
      {modalProduct !== null && <ProductModal product={modalProduct === "new" ? null : modalProduct} onClose={() => setModalProduct(null)} onSaved={() => { qc.invalidateQueries({ queryKey: ["products"] }); setModalProduct(null); }} />}
    </div>
  );
}
