"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Plus, Package, Loader2, AlertTriangle } from "lucide-react";
import { productService } from "@/services/product.service";
import { formatCurrency } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Product } from "@/types";

interface Props {
  onAdd: (product_id: number) => void;
}

export function ProductSearch({ onAdd }: Props) {
  const [search,   setSearch]   = useState("");
  const [category, setCategory] = useState<number | null>(null);
  const [adding,   setAdding]   = useState<number | null>(null);

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn:  productService.getCategories,
    staleTime: Infinity,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["products-pos", search, category],
    queryFn:  () => productService.getProducts({
      search:      search || undefined,
      category_id: category || undefined,
      is_active:   true,
      page_size:   48,
    }),
    enabled: true,
  });

  const handleAdd = async (product: Product) => {
    if (product.stock_qty <= 0) return;
    setAdding(product.id);
    try {
      await onAdd(product.id);
    } finally {
      setAdding(null);
    }
  };

  return (
    <div className="space-y-4">

      {/* Search bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Mahsulot nomi bo'yicha qidirish..."
          className="w-full h-10 pl-9 pr-4 rounded-xl border border-slate-200 dark:border-slate-700
            bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-white
            placeholder-slate-400 focus:outline-none focus:border-brand-500
            focus:ring-1 focus:ring-brand-500 transition"
        />
      </div>

      {/* Category chips */}
      {categories && categories.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setCategory(null)}
            className={cn(
              "px-3 py-1 rounded-full text-xs font-medium transition border",
              category === null
                ? "bg-brand-600 text-white border-brand-600"
                : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-brand-400"
            )}
          >
            Barchasi
          </button>
          {categories.slice(0, 10).map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id === category ? null : cat.id)}
              className={cn(
                "px-3 py-1 rounded-full text-xs font-medium transition border",
                category === cat.id
                  ? "bg-brand-600 text-white border-brand-600"
                  : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-brand-400"
              )}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {/* Product grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-40">
          <Loader2 className="w-6 h-6 text-brand-500 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {data?.results.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAdd={handleAdd}
              isAdding={adding === product.id}
            />
          ))}
          {data?.results.length === 0 && (
            <div className="col-span-full flex flex-col items-center justify-center h-40 text-slate-400">
              <Package className="w-8 h-8 mb-2 opacity-40" />
              <p className="text-sm">Mahsulot topilmadi</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ProductCard({
  product, onAdd, isAdding
}: {
  product: Product;
  onAdd:   (p: Product) => void;
  isAdding:boolean;
}) {
  const outOfStock = product.stock_qty <= 0;
  const isLow      = product.is_low_stock && !outOfStock;

  return (
    <button
      onClick={() => onAdd(product)}
      disabled={outOfStock || isAdding}
      className={cn(
        "group relative flex flex-col bg-white dark:bg-slate-900 rounded-xl border text-left",
        "transition-all duration-150 overflow-hidden",
        outOfStock
          ? "opacity-50 cursor-not-allowed border-slate-200 dark:border-slate-800"
          : "border-slate-200 dark:border-slate-800 hover:border-brand-400 hover:shadow-md hover:shadow-brand-500/10 active:scale-[0.98]"
      )}
    >
      {/* Image / placeholder */}
      <div className="aspect-square w-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden">
        {product.image ? (
          <img src={product.image} alt={product.name}
            className="w-full h-full object-cover" />
        ) : (
          <Package className="w-8 h-8 text-slate-300 dark:text-slate-600" />
        )}

        {/* Add overlay */}
        {!outOfStock && (
          <div className="absolute inset-0 bg-brand-600/0 group-hover:bg-brand-600/5 transition-colors
            flex items-center justify-center">
            {isAdding ? (
              <div className="opacity-0 group-hover:opacity-100 transition w-8 h-8 rounded-full
                bg-brand-600 flex items-center justify-center shadow-lg">
                <Loader2 className="w-4 h-4 text-white animate-spin" />
              </div>
            ) : (
              <div className="opacity-0 group-hover:opacity-100 transition w-8 h-8 rounded-full
                bg-brand-600 flex items-center justify-center shadow-lg">
                <Plus className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        )}

        {/* Stock badge */}
        {isLow && (
          <div className="absolute top-1.5 right-1.5">
            <div className="w-2 h-2 rounded-full bg-amber-400" title="Kam qoldiq" />
          </div>
        )}
        {outOfStock && (
          <div className="absolute top-1.5 right-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-2.5 space-y-0.5">
        <p className="text-xs font-medium text-slate-800 dark:text-white leading-tight line-clamp-2">
          {product.name}
        </p>
        <p className="text-xs font-bold text-brand-600 dark:text-brand-400">
          {formatCurrency(product.sell_price)}
        </p>
        <p className={cn(
          "text-xs",
          outOfStock ? "text-red-400" : isLow ? "text-amber-500" : "text-slate-400"
        )}>
          {outOfStock
            ? "Tugagan"
            : `${product.stock_qty} ${product.unit_short || "d"}`
          }
        </p>
      </div>
    </button>
  );
}
