"use client";
import { useCart } from "@/hooks/useCart";
import {
  ShoppingCart, Trash2, Plus, Minus, X,
  CreditCard, Loader2, PackageOpen,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Cart } from "@/types";

interface Props {
  cart:       Cart;
  isLoading:  boolean;
  onCheckout: () => void;
}

export function CartPanel({ cart, isLoading, onCheckout }: Props) {
  const { updateItem, removeItem, clear } = useCart();

  const isEmpty = cart.items.length === 0;

  return (
    <div className="w-[360px] shrink-0 flex flex-col bg-white dark:bg-slate-900 h-full">

      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <ShoppingCart className="w-4 h-4 text-brand-500" />
          <span className="font-semibold text-slate-800 dark:text-white text-sm">Savat</span>
          {cart.item_count > 0 && (
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full
              bg-brand-600 text-white text-xs font-bold">
              {cart.item_count}
            </span>
          )}
        </div>
        {!isEmpty && (
          <button
            onClick={clear}
            className="flex items-center gap-1 text-xs text-red-400 hover:text-red-500 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Tozalash
          </button>
        )}
      </div>

      {/* Items */}
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
            <PackageOpen className="w-12 h-12 opacity-30" />
            <p className="text-sm">Savat bo'sh</p>
            <p className="text-xs text-slate-300 dark:text-slate-600 text-center px-6">
              Mahsulot qo'shish uchun barcode skanerlang yoki qidiring
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100 dark:divide-slate-800">
            {cart.items.map((item) => (
              <CartItem
                key={item.product_id}
                item={item}
                onUpdate={updateItem}
                onRemove={removeItem}
                isLoading={isLoading}
              />
            ))}
          </ul>
        )}
      </div>

      {/* Footer — total + checkout */}
      <div className="border-t border-slate-200 dark:border-slate-800 p-5 space-y-4">
        {/* Total */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">Jami</span>
          <span className="text-xl font-bold text-slate-800 dark:text-white">
            {formatCurrency(cart.total_amount)}
          </span>
        </div>

        {/* Checkout button */}
        <button
          onClick={onCheckout}
          disabled={isEmpty || isLoading}
          className={cn(
            "w-full h-12 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition",
            isEmpty || isLoading
              ? "bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-not-allowed"
              : "bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-600/25 active:scale-[0.98]"
          )}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <CreditCard className="w-4 h-4" />
              To'lovga o'tish
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function CartItem({
  item, onUpdate, onRemove, isLoading
}: {
  item:      Cart["items"][0];
  onUpdate:  (id: number, qty: number) => void;
  onRemove:  (id: number) => void;
  isLoading: boolean;
}) {
  const qty      = parseFloat(item.quantity);
  const subtotal = parseFloat(item.subtotal);

  return (
    <li className="flex items-start gap-3 px-5 py-3">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-800 dark:text-white leading-snug truncate">
          {item.name}
        </p>
        <p className="text-xs text-slate-400 mt-0.5">
          {formatCurrency(item.sell_price)} × {qty} {item.unit_short}
        </p>
      </div>

      <div className="flex flex-col items-end gap-1.5 shrink-0">
        {/* Subtotal */}
        <span className="text-sm font-bold text-slate-800 dark:text-white">
          {formatCurrency(subtotal)}
        </span>

        {/* Qty controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => qty > 1 ? onUpdate(item.product_id, qty - 1) : onRemove(item.product_id)}
            disabled={isLoading}
            className="w-6 h-6 rounded-md border border-slate-200 dark:border-slate-700
              flex items-center justify-center text-slate-500 hover:text-red-400
              hover:border-red-300 transition disabled:opacity-40"
          >
            {qty <= 1
              ? <X className="w-3 h-3" />
              : <Minus className="w-3 h-3" />
            }
          </button>

          <span className="w-8 text-center text-sm font-medium text-slate-700 dark:text-slate-200">
            {qty}
          </span>

          <button
            onClick={() => onUpdate(item.product_id, qty + 1)}
            disabled={isLoading}
            className="w-6 h-6 rounded-md border border-slate-200 dark:border-slate-700
              flex items-center justify-center text-slate-500 hover:text-brand-500
              hover:border-brand-400 transition disabled:opacity-40"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
      </div>
    </li>
  );
}
