"use client";
import { useQuery } from "@tanstack/react-query";
import {
  TrendingUp, ShoppingCart, Package, AlertTriangle,
  CreditCard, Banknote, Wallet, ArrowUpRight,
} from "lucide-react";
import { dashboardService } from "@/services/dashboard.service";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { useT } from "@/i18n";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";

export default function DashboardPage() {
  const t = useT();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn:  () => dashboardService.getDashboard(7, 5),
    refetchInterval: 60_000,
  });

  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const chartData = data.sales_chart.map((d) => ({
    date:    new Date(d.date).toLocaleDateString("uz-UZ", { month: "short", day: "numeric" }),
    revenue: parseFloat(d.revenue),
    count:   d.count,
  }));

  return (
    <div className="space-y-6">

      {/* Period tabs */}
      <PeriodCards data={data} t={t} />

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Chart — 2 cols */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800 dark:text-white text-sm">
              Oxirgi 7 kun sotuvlar
            </h3>
            <span className="text-xs text-slate-400">so'm</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#0ea5e9" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:opacity-20" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} tickLine={false} axisLine={false}
                tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12 }}
                formatter={(v: any) => [formatCurrency(v), "Tushum"]}
              />
              <Area type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={2}
                fill="url(#grad)" dot={{ r: 3, fill: "#0ea5e9" }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Stock + Debts */}
        <div className="space-y-4">
          <StockCard stock={data.stock} t={t} />
          <DebtCard  debts={data.debts} t={t} />
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <RecentSales  sales={data.recent_sales} t={t} />
        <LowStockList items={data.low_stock}    t={t} />
      </div>
    </div>
  );
}

// ─── Period Cards ─────────────────────────────────────────────────────────────
function PeriodCards({ data, t }: any) {
  const periods = [
    { key: "today", label: t("dashboard.today"), color: "brand" },
    { key: "week",  label: t("dashboard.week"),  color: "violet" },
    { key: "month", label: t("dashboard.month"), color: "emerald" },
    { key: "year",  label: t("dashboard.year"),  color: "amber" },
  ] as const;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {periods.map(({ key, label }) => {
        const s = data[key];
        return (
          <div key={key}
            className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500">{label}</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-300" />
            </div>
            <p className="text-lg font-bold text-slate-800 dark:text-white truncate">
              {formatCurrency(s.revenue)}
            </p>
            <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <ShoppingCart className="w-3 h-3" /> {s.sales_count}
              </span>
              <span className="flex items-center gap-1 text-emerald-500">
                <TrendingUp className="w-3 h-3" /> {formatCurrency(s.gross_profit)}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Stock Card ───────────────────────────────────────────────────────────────
function StockCard({ stock, t }: any) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Package className="w-4 h-4 text-brand-500" />
        <h3 className="text-sm font-semibold text-slate-800 dark:text-white">Ombor</h3>
      </div>
      <div className="space-y-2 text-sm">
        <Row label="Jami mahsulot"    value={`${stock.total_products} ta`} />
        <Row label="Kam qoldiq"       value={`${stock.low_stock_count} ta`} valueClass="text-amber-500" />
        <Row label="Tugagan"          value={`${stock.out_of_stock} ta`}   valueClass="text-red-500" />
        <Row label="Sotuv qiymati"    value={formatCurrency(stock.sell_value)} />
      </div>
    </div>
  );
}

// ─── Debt Card ────────────────────────────────────────────────────────────────
function DebtCard({ debts, t }: any) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Wallet className="w-4 h-4 text-red-400" />
        <h3 className="text-sm font-semibold text-slate-800 dark:text-white">Qarzlar</h3>
      </div>
      <div className="space-y-2 text-sm">
        <Row label="Jami qarz"         value={formatCurrency(debts.total_debt)} valueClass="text-red-400" />
        <Row label="Xaridlar soni"     value={`${debts.count} ta`} />
        <Row label="Muddati o'tgan"    value={formatCurrency(debts.overdue_debt)} valueClass="text-orange-400" />
      </div>
    </div>
  );
}

// ─── Recent Sales ─────────────────────────────────────────────────────────────
function RecentSales({ sales, t }: any) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5">
      <h3 className="text-sm font-semibold text-slate-800 dark:text-white mb-3">
        So'nggi sotuvlar
      </h3>
      <div className="space-y-2">
        {sales.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-4">Hali sotuv yo'q</p>
        )}
        {sales.map((s: any) => (
          <div key={s.id} className="flex items-center justify-between py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
            <div>
              <p className="text-xs font-medium text-slate-700 dark:text-slate-200">{s.invoice_no}</p>
              <p className="text-xs text-slate-400">{s.cashier__full_name ?? "—"} · {formatDateTime(s.created_at)}</p>
            </div>
            <span className="text-xs font-semibold text-brand-500">{formatCurrency(s.net_amount)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Low Stock ────────────────────────────────────────────────────────────────
function LowStockList({ items, t }: any) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle className="w-4 h-4 text-amber-400" />
        <h3 className="text-sm font-semibold text-slate-800 dark:text-white">Kam qoldiqlar</h3>
      </div>
      <div className="space-y-2">
        {items.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-4">Hammasi yetarli ✓</p>
        )}
        {items.map((item: any) => (
          <div key={item.product__id} className="flex items-center justify-between py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
            <p className="text-xs font-medium text-slate-700 dark:text-slate-200 truncate flex-1 mr-3">
              {item.product__name}
            </p>
            <div className="text-right shrink-0">
              <span className="text-xs font-bold text-red-400">{item.quantity}</span>
              <span className="text-xs text-slate-400"> / {item.product__min_stock}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Row({ label, value, valueClass = "text-slate-700 dark:text-slate-200" }: any) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-400">{label}</span>
      <span className={`font-medium ${valueClass}`}>{value}</span>
    </div>
  );
}
