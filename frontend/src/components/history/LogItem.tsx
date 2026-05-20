"use client";
import {
  LogIn, LogOut, ShoppingCart, Package,
  Settings, AlertTriangle, Warehouse, Building2,
} from "lucide-react";
import { formatDateTime, cn } from "@/lib/utils";
import type { AuditLog } from "@/services/history.service";

const ACTION_CONFIG: Record<string, { Icon: React.ElementType; color: string; bg: string }> = {
  login:            { Icon: LogIn,        color: "text-emerald-600", bg: "bg-emerald-50 dark:bg-emerald-950/30" },
  logout:           { Icon: LogOut,       color: "text-slate-500",   bg: "bg-slate-100 dark:bg-slate-800"       },
  sale_checkout:    { Icon: ShoppingCart, color: "text-blue-600",    bg: "bg-blue-50 dark:bg-blue-950/30"       },
  create:           { Icon: Package,      color: "text-brand-600",   bg: "bg-brand-50 dark:bg-brand-950/30"     },
  update:           { Icon: Settings,     color: "text-amber-600",   bg: "bg-amber-50 dark:bg-amber-950/30"     },
  delete:           { Icon: AlertTriangle,color: "text-red-500",     bg: "bg-red-50 dark:bg-red-950/30"         },
  purchase_receive: { Icon: Warehouse,    color: "text-violet-600",  bg: "bg-violet-50 dark:bg-violet-950/30"   },
  purchase_pay:     { Icon: Building2,    color: "text-emerald-600", bg: "bg-emerald-50 dark:bg-emerald-950/30" },
};

export const MODEL_LABELS: Record<string, string> = {
  sale:     "Sotuv",
  product:  "Mahsulot",
  purchase: "Xarid",
  user:     "Foydalanuvchi",
  company:  "Kompaniya",
  stock:    "Ombor",
};

interface Props {
  log:        AuditLog;
  isExpanded: boolean;
  onToggle:   () => void;
}

export function LogItem({ log, isExpanded, onToggle }: Props) {
  const cfg      = ACTION_CONFIG[log.action] ?? ACTION_CONFIG.create;
  const hasExtra = log.extra && Object.keys(log.extra).length > 0;

  return (
    <li>
      <button
        onClick={hasExtra ? onToggle : undefined}
        className={cn(
          "w-full flex items-start gap-3 px-4 py-3.5 text-left transition",
          hasExtra
            ? "hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer"
            : "cursor-default"
        )}
      >
        {/* Icon */}
        <div className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5",
          cfg.bg
        )}>
          <cfg.Icon className={cn("w-4 h-4", cfg.color)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-medium text-slate-800 dark:text-white">
                {log.action_display}
              </span>
              {log.model_name && (
                <span className="px-1.5 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 text-slate-500">
                  {MODEL_LABELS[log.model_name.toLowerCase()] ?? log.model_name}
                </span>
              )}
            </div>
            <span className="text-xs text-slate-400 shrink-0">
              {formatDateTime(log.created_at)}
            </span>
          </div>

          <div className="flex items-center gap-3 mt-0.5 flex-wrap">
            {log.user_name && (
              <span className="text-xs text-slate-500">{log.user_name}</span>
            )}
            {log.object_repr && (
              <span className="text-xs text-slate-400 truncate max-w-[200px]">
                {log.object_repr}
              </span>
            )}
            {log.ip_address && (
              <span className="text-xs text-slate-300 dark:text-slate-600 font-mono">
                {log.ip_address}
              </span>
            )}
          </div>

          {/* Expanded extra */}
          {isExpanded && hasExtra && (
            <div className="mt-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-1">
              {Object.entries(log.extra).map(([key, value]) => (
                <div key={key} className="flex gap-2 text-xs">
                  <span className="text-slate-400 shrink-0 min-w-[80px]">{key}:</span>
                  <span className="text-slate-600 dark:text-slate-300 font-mono break-all">
                    {typeof value === "object" ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {hasExtra && (
          <span className="text-xs text-slate-300 dark:text-slate-600 shrink-0 mt-1">
            {isExpanded ? "▲" : "▼"}
          </span>
        )}
      </button>
    </li>
  );
}
