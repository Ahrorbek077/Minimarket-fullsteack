"use client";
import { useEffect, useState, useCallback } from "react";
import { useCart } from "@/hooks/useCart";
import { useBarcode } from "@/hooks/useBarcode";
import { ProductSearch } from "@/components/pos/ProductSearch";
import { CartPanel } from "@/components/pos/CartPanel";
import { CheckoutModal } from "@/components/pos/CheckoutModal";
import { ReceiptModal } from "@/components/pos/ReceiptModal";
import { ScannerInput } from "@/components/pos/ScannerInput";
import type { Sale } from "@/types";

export default function POSPage() {
  const { cart, fetchCart, scan, addItem, isLoading } = useCart();
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [receipt,      setReceipt]      = useState<Sale | null>(null);

  useEffect(() => { fetchCart(); }, [fetchCart]);

  // USB/BT scanner global listener
  useBarcode(useCallback((barcode: string) => scan(barcode), [scan]));

  const handleCheckoutDone = (sale: Sale) => {
    setCheckoutOpen(false);
    setReceipt(sale);
  };

  return (
    <div className="flex h-full -m-6 overflow-hidden">

      {/* Left — search + products */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50 dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800">
        <ScannerInput onScan={scan} isLoading={isLoading} />
        <div className="flex-1 overflow-y-auto p-5">
          <ProductSearch onAdd={addItem} />
        </div>
      </div>

      {/* Right — cart */}
      <CartPanel
        cart={cart}
        isLoading={isLoading}
        onCheckout={() => setCheckoutOpen(true)}
      />

      {checkoutOpen && (
        <CheckoutModal
          cart={cart}
          onClose={() => setCheckoutOpen(false)}
          onDone={handleCheckoutDone}
        />
      )}
      {receipt && (
        <ReceiptModal
          sale={receipt}
          onClose={() => setReceipt(null)}
        />
      )}
    </div>
  );
}
