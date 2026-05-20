"use client";
import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  X, Printer, RotateCcw, Loader2,
  Receipt, User, CalendarDays, Banknote,
  CreditCard, Wallet, Package, AlertCircle,
} from "lucide-react";
import { saleService } from "@/services/sale.service";
import { formatCurrency, formatDateTime, cn } from "@/lib/utils";
import type { Sale } from "@/types";

const METHOD_CONFIG: Record<string, { label: string; Icon: React.ElementType }> = {
  cash: { label: "Naqd",   Icon: Banknote   },
  card: { label: "Karta",  Icon: CreditCard },
  debt: { label: "Nasiya", Icon: Wallet     },
};

interface Props {
  sale:        Sale;
  onClose:     () => void;
  onReturn:    (id: number, reason: string) => void;
  isReturning: boolean;
}

export function SaleDetailDrawer({ sale, onClose, onReturn, isReturning }: Props) {
  const printRef    = useRef<HTMLDivElement>(null);
  const [showReturn, setShowReturn] = useState(false);
  const [reason,     setReason]     = useState("");

  const { data: detail, isLoading } = useQuery({
    queryKey: ["sale-detail", sale.id],
    queryFn:  () => saleService.getById(sale.id),
  });

  const canReturn = sale.status === "completed";

  // ── Print receipt ────────────────────────────────────────────────────────
  const handlePrint = () => {
    if (!printRef.current) return;
    const win = window.open("", "_blank", "width=400,height=600");
    if (!win) return;
    win.document.write(`<!DOCTYPE html><html><head>
      <title>Chek #${sale.invoice_no}</title>
      <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Courier New', monospace; font-size: 12px; width: 80mm; margin: 0 auto; padding: 8px; }
        .center { text-align: center; }
        .bold   { font-weight: bold; }
        .large  { font-size: 15px; font-weight: bold; }
        .hr     { border-top: 1px dashed #000; margin: 6px 0; }
        .row    { display: flex; justify-content: space-between; margin: 2px 0; }
        .right  { text-align: right; }
        table   { width: 100%; border-collapse: collapse; font-size: 11px; }
        td      { padding: 2px 4px; }
      </style></head>
      <body>${printRef.current.innerHTML}</body></html>`
    );
    win.document.close();
    setTimeout(() => { win.print(); win.close(); }, 300);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <Receipt className="w-4 h-4 text-brand-500" />
              <h2 className="font-semibold text-slate-800 dark:text-white">Sotuv tafsiloti</h2>
            </div>
            <p className="text-xs font-mono text-brand-600 dark:text-brand-400 mt-0.5">
              #{sale.invoice_no}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handlePrint}
              className="flex items-center gap-1.5 h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              <Printer className="w-3.5 h-3.5" />
              Chop etish
            </button>
            <button onClick={onClose}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">

          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
            </div>
          ) : detail ? (
            <>
              {/* Info cards */}
              <div className="grid grid-cols-2 gap-3">
                <InfoCard icon={CalendarDays} label="Sana" value={formatDateTime(sale.created_at)} />
                <InfoCard icon={User}         label="Kassir" value={sale.cashier_name ?? "—"} />
              </div>

              {/* Amount summary */}
              <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2 text-sm">
                <div className="flex justify-between text-slate-600 dark:text-slate-400">
                  <span>Umumiy</span>
                  <span>{formatCurrency(sale.total_amount)}</span>
                </div>
                {parseFloat(sale.discount_amount) > 0 && (
                  <div className="flex justify-between text-emerald-600">
                    <span>Chegirma ({sale.discount_pct}%)</span>
                    <span>−{formatCurrency(sale.discount_amount)}</span>
                  </div>
                )}
                <div className="flex justify-between font-bold text-slate-800 dark:text-white border-t border-slate-200 dark:border-slate-700 pt-2">
                  <span>To'langan</span>
                  <span className="text-base">{formatCurrency(sale.net_amount)}</span>
                </div>
                {parseFloat(sale.debt_amount) > 0 && (
                  <div className="flex justify-between text-amber-600 font-medium">
                    <span>Nasiya qoldig'i</span>
                    <span>{formatCurrency(sale.debt_amount)}</span>
                  </div>
                )}
              </div>

              {/* Payment methods */}
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">To'lov usullari</p>
                <div className="flex gap-2 flex-wrap">
                  {detail.payments.map((p) => {
                    const cfg = METHOD_CONFIG[p.method] ?? METHOD_CONFIG.cash;
                    return (
                      <div key={p.id}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <cfg.Icon className="w-3.5 h-3.5 text-slate-500" />
                        <div>
                          <p className="text-xs font-medium text-slate-700 dark:text-slate-200">{cfg.label}</p>
                          <p className="text-xs text-slate-400 font-mono">{formatCurrency(p.amount)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Items table */}
              <div>
                <p className="text-xs font-medium text-slate-500 mb-2">
                  Mahsulotlar ({detail.items.length} ta)
                </p>
                <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
                        <th className="px-3 py-2 text-left text-slate-500 font-medium">Mahsulot</th>
                        <th className="px-3 py-2 text-right text-slate-500 font-medium">Miqdor</th>
                        <th className="px-3 py-2 text-right text-slate-500 font-medium">Narx</th>
                        <th className="px-3 py-2 text-right text-slate-500 font-medium">Jami</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {detail.items.map((item) => (
                        <tr key={item.id} className="bg-white dark:bg-slate-900">
                          <td className="px-3 py-2 text-slate-700 dark:text-slate-200 font-medium max-w-[140px] truncate">
                            {item.product_name}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-500">
                            {item.quantity} {item.unit_short}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-500 font-mono">
                            {formatCurrency(item.sell_price)}
                          </td>
                          <td className="px-3 py-2 text-right font-semibold text-slate-700 dark:text-slate-200 font-mono">
                            {formatCurrency(item.total)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Note */}
              {detail.note && (
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
                  <p className="text-xs text-slate-500 mb-0.5">Izoh</p>
                  <p className="text-sm text-slate-700 dark:text-slate-200">{detail.note}</p>
                </div>
              )}

              {/* Return section */}
              {canReturn && (
                <div className="border border-red-200 dark:border-red-800/60 rounded-xl overflow-hidden">
                  {!showReturn ? (
                    <button
                      onClick={() => setShowReturn(true)}
                      className="w-full flex items-center gap-2 px-4 py-3 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 transition"
                    >
                      <RotateCcw className="w-4 h-4" />
                      Sotuvni qaytarish
                    </button>
                  ) : (
                    <div className="p-4 space-y-3 bg-red-50 dark:bg-red-950/20">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                        <p className="text-xs text-red-600 dark:text-red-400">
                          Sotuv qaytarilsa mahsulotlar omborga qaytadi va sotuv "Qaytarilgan" holatiga o'tadi.
                        </p>
                      </div>
                      <textarea
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Qaytarish sababini kiriting..."
                        rows={2}
                        className="w-full px-3 py-2 rounded-lg border border-red-200 dark:border-red-800 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-red-400 resize-none transition"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowReturn(false)}
                          className="flex-1 h-9 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-white dark:hover:bg-slate-800 transition"
                        >
                          Bekor
                        </button>
                        <button
                          onClick={() => onReturn(sale.id, reason)}
                          disabled={isReturning || reason.trim().length < 3}
                          className="flex-1 h-9 rounded-lg bg-red-500 hover:bg-red-600 text-white text-sm font-medium flex items-center justify-center gap-1.5 transition disabled:opacity-50"
                        >
                          {isReturning
                            ? <Loader2 className="w-4 h-4 animate-spin" />
                            : <><RotateCcw className="w-3.5 h-3.5" />Tasdiqlash</>
                          }
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Hidden printable receipt */}
        <div className="hidden">
          <div ref={printRef}>
            <div className="center bold large">Mini Market</div>
            <div className="center" style={{ fontSize: "11px", color: "#666" }}>POS tizimi</div>
            <div className="hr" />
            <div className="row"><span>Chek #</span><span className="bold">{sale.invoice_no}</span></div>
            <div className="row"><span>Sana</span><span>{formatDateTime(sale.created_at)}</span></div>
            {sale.cashier_name && <div className="row"><span>Kassir</span><span>{sale.cashier_name}</span></div>}
            <div className="hr" />
            {detail?.items.map((item) => (
              <div key={item.id}>
                <div style={{ fontWeight: "bold", marginBottom: "1px" }}>{item.product_name}</div>
                <div className="row">
                  <span>{item.quantity} × {formatCurrency(item.sell_price)}</span>
                  <span className="bold">{formatCurrency(item.total)}</span>
                </div>
              </div>
            ))}
            <div className="hr" />
            <div className="row"><span>Jami</span><span>{formatCurrency(sale.total_amount)}</span></div>
            {parseFloat(sale.discount_amount) > 0 && (
              <div className="row">
                <span>Chegirma ({sale.discount_pct}%)</span>
                <span>−{formatCurrency(sale.discount_amount)}</span>
              </div>
            )}
            <div className="row bold" style={{ fontSize: "14px", marginTop: "4px" }}>
              <span>TO'LANDI</span>
              <span>{formatCurrency(sale.net_amount)}</span>
            </div>
            {parseFloat(sale.debt_amount) > 0 && (
              <div className="row"><span>Nasiya</span><span>{formatCurrency(sale.debt_amount)}</span></div>
            )}
            <div className="hr" />
            {detail?.payments.map((p) => (
              <div key={p.id} className="row">
                <span>{METHOD_CONFIG[p.method]?.label ?? p.method}</span>
                <span>{formatCurrency(p.amount)}</span>
              </div>
            ))}
            <div className="hr" />
            <div className="center" style={{ marginTop: "8px", fontSize: "11px" }}>
              Xarid uchun rahmat!
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-3">
      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
        <Icon className="w-3.5 h-3.5" />
        {label}
      </div>
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{value}</p>
    </div>
  );
}
