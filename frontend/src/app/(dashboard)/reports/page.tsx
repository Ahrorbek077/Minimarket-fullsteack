"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  FileSpreadsheet, FileText, Download, BarChart2,
  TrendingUp, Package, Wallet, Loader2, CalendarDays,
} from "lucide-react";
import { reportService, type ReportType, type ReportFormat } from "@/services/report.service";
import { formatCurrency, cn } from "@/lib/utils";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

// ── Date helpers ─────────────────────────────────────────────────────────────
function today()    { return new Date().toISOString().slice(0, 10); }
function daysAgo(n: number) {
  const d = new Date(); d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

export default function ReportsPage() {
  const [dateFrom, setDateFrom] = useState(daysAgo(29));
  const [dateTo,   setDateTo]   = useState(today());
  const [period,   setPeriod]   = useState<"daily"|"weekly"|"monthly">("daily");
  const [downloading, setDownloading] = useState<string | null>(null);

  // Summary
  const { data: summary } = useQuery({
    queryKey: ["report-summary", dateFrom, dateTo],
    queryFn:  () => reportService.getSalesSummary(dateFrom, dateTo),
    enabled:  !!dateFrom && !!dateTo,
  });

  // Chart
  const { data: chartData } = useQuery({
    queryKey: ["report-chart", dateFrom, dateTo, period],
    queryFn:  () => reportService.getSalesChart(dateFrom, dateTo, period),
    enabled:  !!dateFrom && !!dateTo,
  });

  // Top products
  const { data: topProducts } = useQuery({
    queryKey: ["report-top", dateFrom, dateTo],
    queryFn:  () => reportService.getTopProducts(dateFrom, dateTo, 8),
    enabled:  !!dateFrom && !!dateTo,
  });

  // Stock summary
  const { data: stockSummary } = useQuery({
    queryKey: ["report-stock"],
    queryFn:  reportService.getStockSummary,
  });

  // ── Export ──────────────────────────────────────────────────────────────
  const handleExport = async (type: ReportType, fmt: ReportFormat) => {
    const key = `${type}-${fmt}`;
    setDownloading(key);
    try {
      const blob = await reportService.export({
        file_format: fmt,
        type,
        date_from: dateFrom,
        date_to:   dateTo,
      });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `${type}_${dateFrom}_${dateTo}.${fmt === "excel" ? "xlsx" : "pdf"}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Fayl yuklab olindi");
    } catch {
      toast.error("Export xatosi yuz berdi");
    } finally {
      setDownloading(null);
    }
  };

  // Chart format
  const formattedChart = (chartData as any[])?.map((d: any) => ({
    name:    d.date ?? d.period ?? "—",
    revenue: parseFloat(d.revenue ?? "0"),
    count:   d.count ?? 0,
  })) ?? [];

  const formattedTop = (topProducts as any[])?.map((p: any) => ({
    name:    (p.product__name as string)?.slice(0, 16) + ((p.product__name as string)?.length > 16 ? "…" : ""),
    revenue: parseFloat(p.total_revenue ?? "0"),
    qty:     parseFloat(p.total_qty ?? "0"),
  })) ?? [];

  return (
    <div className="space-y-6">

      {/* Date range + period */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <CalendarDays className="w-4 h-4 text-slate-400 shrink-0" />
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
              className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition w-36" />
            <span className="text-slate-400">—</span>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
              className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition w-36" />
          </div>

          {/* Quick presets */}
          <div className="flex gap-1.5 flex-wrap">
            {[
              { label: "Bugun",      from: today(),     to: today()    },
              { label: "7 kun",      from: daysAgo(6),  to: today()    },
              { label: "30 kun",     from: daysAgo(29), to: today()    },
              { label: "Bu oy",      from: today().slice(0,7)+"-01", to: today() },
            ].map(({ label, from, to }) => (
              <button key={label}
                onClick={() => { setDateFrom(from); setDateTo(to); }}
                className={cn(
                  "h-7 px-2.5 rounded-lg border text-xs font-medium transition",
                  dateFrom === from && dateTo === to
                    ? "bg-brand-600 text-white border-brand-600"
                    : "border-slate-200 dark:border-slate-700 text-slate-500 hover:border-brand-400"
                )}>
                {label}
              </button>
            ))}
          </div>

          {/* Period */}
          <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden ml-auto">
            {(["daily","weekly","monthly"] as const).map((p) => (
              <button key={p} onClick={() => setPeriod(p)}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium transition",
                  period === p ? "bg-brand-600 text-white" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}>
                {p === "daily" ? "Kunlik" : p === "weekly" ? "Haftalik" : "Oylik"}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: BarChart2,  label: "Jami sotuvlar",  value: String((summary as any)?.sales_count ?? 0),            color: "blue"   },
          { icon: TrendingUp, label: "Tushum",         value: formatCurrency((summary as any)?.revenue ?? 0),         color: "green"  },
          { icon: TrendingUp, label: "Foyda",          value: formatCurrency((summary as any)?.gross_profit ?? 0),    color: "emerald"},
          { icon: Wallet,     label: "Nasiya",         value: formatCurrency((summary as any)?.debt ?? 0),            color: "amber"  },
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

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Sales chart */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-white mb-4">Sotuvlar dinamikasi</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={formattedChart}>
              <defs>
                <linearGradient id="rg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#0ea5e9" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}   />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:opacity-20" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#94a3b8" }} tickLine={false} axisLine={false}
                tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12 }}
                formatter={(v: any) => [formatCurrency(v), "Tushum"]}
              />
              <Area type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={2}
                fill="url(#rg)" dot={{ r: 2.5, fill: "#0ea5e9" }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Top products chart */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-white mb-4">Top mahsulotlar</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={formattedTop} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:opacity-20" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: "#94a3b8" }} tickLine={false} axisLine={false}
                tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }} tickLine={false} axisLine={false} width={60} />
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12 }}
                formatter={(v: any) => [formatCurrency(v), "Tushum"]} />
              <Bar dataKey="revenue" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stock summary + Export */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Stock summary */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Package className="w-4 h-4 text-brand-500" />
            <h3 className="text-sm font-semibold text-slate-800 dark:text-white">Ombor holati</h3>
          </div>
          <div className="space-y-2.5 text-sm">
            {[
              { label: "Jami mahsulot",    value: (stockSummary as any)?.total_products  ?? "—" },
              { label: "Kam qoldiq",       value: (stockSummary as any)?.low_stock_count ?? "—", cls: "text-amber-500" },
              { label: "Tugagan",          value: (stockSummary as any)?.out_of_stock    ?? "—", cls: "text-red-500"   },
              { label: "Tan narx qiymati", value: formatCurrency((stockSummary as any)?.cost_value ?? 0) },
              { label: "Sotuv qiymati",    value: formatCurrency((stockSummary as any)?.sell_value ?? 0), cls: "text-emerald-600" },
            ].map(({ label, value, cls }) => (
              <div key={label} className="flex justify-between">
                <span className="text-slate-500">{label}</span>
                <span className={cn("font-medium text-slate-700 dark:text-slate-200", cls)}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Export buttons */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Download className="w-4 h-4 text-brand-500" />
            <h3 className="text-sm font-semibold text-slate-800 dark:text-white">Hisobotlarni yuklab olish</h3>
          </div>
          <div className="space-y-2.5">
            {([
              { type: "sales"       as ReportType, label: "Sotuvlar hisoboti",    icon: TrendingUp    },
              { type: "purchases"   as ReportType, label: "Xaridlar hisoboti",    icon: Package       },
              { type: "stock"       as ReportType, label: "Ombor hisoboti",       icon: Package       },
              { type: "top_products"as ReportType, label: "Top mahsulotlar",      icon: BarChart2     },
            ]).map(({ type, label, icon: Icon }) => (
              <div key={type} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-700 dark:text-slate-200">{label}</span>
                </div>
                <div className="flex gap-1.5">
                  {(["excel","pdf"] as ReportFormat[]).map((fmt) => {
                    const key  = `${type}-${fmt}`;
                    const busy = downloading === key;
                    return (
                      <button
                        key={fmt}
                        onClick={() => handleExport(type, fmt)}
                        disabled={!!downloading}
                        className={cn(
                          "flex items-center gap-1 h-7 px-2.5 rounded-lg border text-xs font-medium transition",
                          fmt === "excel"
                            ? "border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                            : "border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30",
                          downloading && !busy ? "opacity-40" : ""
                        )}>
                        {busy
                          ? <Loader2 className="w-3 h-3 animate-spin" />
                          : fmt === "excel"
                            ? <FileSpreadsheet className="w-3 h-3" />
                            : <FileText className="w-3 h-3" />
                        }
                        {fmt === "excel" ? "Excel" : "PDF"}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-3">
            * Tanlangan sana oralig'i uchun yuklab olinadi: {dateFrom} — {dateTo}
          </p>
        </div>
      </div>
    </div>
  );
}
