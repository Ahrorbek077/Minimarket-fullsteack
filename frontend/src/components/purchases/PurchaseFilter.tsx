"use client";
import { useState } from "react";
import { X, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import type { PurchaseStatus } from "@/types";

const STATUSES: { value: PurchaseStatus; label: string }[] = [
  { value: "draft",     label: "Qoralama"        },
  { value: "received",  label: "Qabul qilindi"   },
  { value: "partial",   label: "Qisman to'landi" },
  { value: "paid",      label: "To'landi"        },
  { value: "cancelled", label: "Bekor qilindi"   },
];

interface Props {
  filters:  Record<string, string>;
  onApply:  (f: Record<string, string>) => void;
  onClose:  () => void;
}

export function PurchaseFilter({ filters, onApply, onClose }: Props) {
  const [local, setLocal] = useState<Record<string, string>>({ ...filters });

  const set = (key: string, val: string) =>
    setLocal((prev) =>
      val === "" ? (({ [key]: _, ...rest }) => rest)(prev) : { ...prev, [key]: val }
    );

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-brand-500" />
            <h3 className="font-semibold text-slate-800 dark:text-white text-sm">Filtr</h3>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Status */}
          <div>
            <label className="text-xs font-medium text-slate-500 mb-2 block">Holat</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => set("status", "")}
                className={cn(
                  "px-3 py-1.5 rounded-lg border text-xs font-medium transition",
                  !local.status
                    ? "bg-brand-600 text-white border-brand-600"
                    : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-brand-400"
                )}
              >
                Barchasi
              </button>
              {STATUSES.map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => set("status", local.status === value ? "" : value)}
                  className={cn(
                    "px-3 py-1.5 rounded-lg border text-xs font-medium transition",
                    local.status === value
                      ? "bg-brand-600 text-white border-brand-600"
                      : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-brand-400"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Overdue toggle */}
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={local.is_overdue === "true"}
                onChange={(e) => set("is_overdue", e.target.checked ? "true" : "")}
              />
              <div className="w-9 h-5 rounded-full bg-slate-200 dark:bg-slate-700 peer-checked:bg-brand-600 transition-colors" />
              <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
            </div>
            <span className="text-sm text-slate-600 dark:text-slate-300">
              Faqat muddati o'tganlar
            </span>
          </label>

          {/* Has debt toggle */}
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={local.has_debt === "true"}
                onChange={(e) => set("has_debt", e.target.checked ? "true" : "")}
              />
              <div className="w-9 h-5 rounded-full bg-slate-200 dark:bg-slate-700 peer-checked:bg-brand-600 transition-colors" />
              <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
            </div>
            <span className="text-sm text-slate-600 dark:text-slate-300">
              Faqat qarzlilar
            </span>
          </label>

          {/* Date range */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-500 mb-1.5 block">Boshlanish</label>
              <input
                type="date"
                value={local.date_from ?? ""}
                onChange={(e) => set("date_from", e.target.value)}
                className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500 mb-1.5 block">Tugash</label>
              <input
                type="date"
                value={local.date_to ?? ""}
                onChange={(e) => set("date_to", e.target.value)}
                className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 pb-5 flex gap-3">
          <button
            onClick={() => setLocal({})}
            className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            Tozalash
          </button>
          <button
            onClick={() => onApply(local)}
            className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition shadow-sm shadow-brand-600/20"
          >
            Qo'llash {Object.keys(local).length > 0 && `(${Object.keys(local).length})`}
          </button>
        </div>
      </div>
    </div>
  );
}
