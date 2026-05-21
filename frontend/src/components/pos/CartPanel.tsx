"use client";
import { useState } from "react";
import { useCart } from "@/hooks/useCart";
import {
  ShoppingCart, Trash2, Plus, Minus, X,
  CreditCard, Loader2, PackageOpen, ChevronDown,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Cart } from "@/types";

// Butun son biriliklar
const INTEGER_UNITS = ["dona", "pkt", "quti", "blok", "pch", "d"];
// kg/g juftlari
const KG_UNITS  = ["kg"];
const G_UNITS   = ["g"];
const L_UNITS   = ["l", "litr"];
const ML_UNITS  = ["ml", "millilitr"];

function isIntegerUnit(unit: string | null) {
  return INTEGER_UNITS.includes((unit ?? "").toLowerCase());
}

function getStep(unit: string | null): number {
  const u = (unit ?? "").toLowerCase();
  if (KG_UNITS.includes(u))  return 0.1;
  if (G_UNITS.includes(u))   return 100;
  if (L_UNITS.includes(u))   return 0.1;
  if (ML_UNITS.includes(u))  return 100;
  if (u === "m")             return 0.1;
  if (u === "sm")            return 10;
  return 1;
}

function formatQty(qty: number, unit: string | null): string {
  if (isIntegerUnit(unit)) return String(qty);
  const u = (unit ?? "").toLowerCase();
  if (KG_UNITS.includes(u) || L_UNITS.includes(u) || u === "m") return qty.toFixed(3).replace(/\.?0+$/, "");
  return String(qty);
}

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
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-brand-600 text-white text-xs font-bold">
              {cart.item_count}
            </span>
          )}
        </div>
        {!isEmpty && (
          <button onClick={clear} className="flex items-center gap-1 text-xs text-red-400 hover:text-red-500 transition">
            <Trash2 className="w-3.5 h-3.5" /> Tozalash
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

      {/* Footer */}
      <div className="border-t border-slate-200 dark:border-slate-800 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">Jami</span>
          <span className="text-xl font-bold text-slate-800 dark:text-white">
            {formatCurrency(cart.total_amount)}
          </span>
        </div>
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
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><CreditCard className="w-4 h-4" />To'lovga o'tish</>}
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
  const unit     = item.unit_short;
  const isInt    = isIntegerUnit(unit);
  const isKg     = KG_UNITS.includes((unit ?? "").toLowerCase());
  const isLitre  = L_UNITS.includes((unit ?? "").toLowerCase());
  const step     = getStep(unit);

  const [inputMode, setInputMode]   = useState(false);
  const [inputVal,  setInputVal]    = useState("");
  // kg → gram mode toggle
  const [gramMode,  setGramMode]    = useState(false);

  const qty      = parseFloat(item.quantity);
  const subtotal = parseFloat(item.subtotal);

  // Effective birlik (gramMode da g ko'rsatamiz)
  const displayUnit = gramMode ? "g" : unit;
  const displayQty  = gramMode ? qty * 1000 : qty;

  const handleAdd = () => {
    const newQty = gramMode
      ? parseFloat(((qty * 1000 + 100) / 1000).toFixed(3))
      : parseFloat((qty + step).toFixed(3));
    onUpdate(item.product_id, newQty);
  };

  const handleMinus = () => {
    const minStep = gramMode ? 0.1 : step;
    const newQty  = gramMode
      ? parseFloat(((qty * 1000 - 100) / 1000).toFixed(3))
      : parseFloat((qty - step).toFixed(3));
    if (newQty <= 0) { onRemove(item.product_id); return; }
    onUpdate(item.product_id, newQty);
  };

  const handleInputConfirm = () => {
    const val = parseFloat(inputVal.replace(",", "."));
    if (!isNaN(val) && val > 0) {
      const finalQty = gramMode ? parseFloat((val / 1000).toFixed(3)) : val;
      onUpdate(item.product_id, finalQty);
    }
    setInputMode(false);
    setInputVal("");
  };

  return (
    <li className="px-5 py-3 space-y-2">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-800 dark:text-white leading-snug truncate">
            {item.name}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            {formatCurrency(item.sell_price)} × {formatQty(displayQty, displayUnit)} {displayUnit}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className="text-sm font-bold text-slate-800 dark:text-white">
            {formatCurrency(subtotal)}
          </span>
          {/* kg/L uchun birlik toggle */}
          {(isKg || isLitre) && (
            <button
              onClick={() => setGramMode(p => !p)}
              className="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-0.5 transition"
            >
              {gramMode ? (isKg ? "kg" : "L") : (isKg ? "g" : "mL")}
              <ChevronDown className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Qty controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleMinus}
          disabled={isLoading}
          className="w-7 h-7 rounded-lg border border-slate-200 dark:border-slate-700
            flex items-center justify-center text-slate-500 hover:text-red-400
            hover:border-red-300 transition disabled:opacity-40"
        >
          {qty <= step ? <X className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
        </button>

        {/* Miqdor — bosib o'zgartirish */}
        {inputMode ? (
          <input
            autoFocus
            type="number"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onBlur={handleInputConfirm}
            onKeyDown={(e) => e.key === "Enter" && handleInputConfirm()}
            step={isInt ? 1 : 0.001}
            min={isInt ? 1 : 0.001}
            className="w-16 h-7 text-center text-sm font-medium border border-brand-400 rounded-lg
              focus:outline-none focus:ring-1 focus:ring-brand-500
              bg-white dark:bg-slate-800 text-slate-800 dark:text-white"
            placeholder={formatQty(displayQty, displayUnit)}
          />
        ) : (
          <button
            onClick={() => { setInputMode(true); setInputVal(String(displayQty)); }}
            className="min-w-[3rem] px-2 h-7 text-center text-sm font-medium text-slate-700
              dark:text-slate-200 border border-transparent hover:border-brand-300
              hover:bg-brand-50 dark:hover:bg-brand-950/20 rounded-lg transition"
            title="Bosib o'zgartirish"
          >
            {formatQty(displayQty, displayUnit)} <span className="text-xs text-slate-400">{displayUnit}</span>
          </button>
        )}

        <button
          onClick={handleAdd}
          disabled={isLoading}
          className="w-7 h-7 rounded-lg border border-slate-200 dark:border-slate-700
            flex items-center justify-center text-slate-500 hover:text-brand-500
            hover:border-brand-400 transition disabled:opacity-40"
        >
          <Plus className="w-3 h-3" />
        </button>

        <button
          onClick={() => onRemove(item.product_id)}
          disabled={isLoading}
          className="ml-auto w-6 h-6 flex items-center justify-center text-slate-300
            hover:text-red-400 transition"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </li>
  );
}
