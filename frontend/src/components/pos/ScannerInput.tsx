"use client";
import { useState, useRef } from "react";
import { Scan, Search, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onScan:    (barcode: string) => void;
  isLoading: boolean;
}

export function ScannerInput({ onScan, isLoading }: Props) {
  const [value, setValue]   = useState("");
  const [mode,  setMode]    = useState<"scan" | "manual">("scan");
  const inputRef            = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const v = value.trim();
    if (v.length >= 3) {
      onScan(v);
      setValue("");
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-5 py-3">
      <form onSubmit={handleSubmit} className="flex items-center gap-3">

        {/* Mode toggle */}
        <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden shrink-0">
          <button
            type="button"
            onClick={() => setMode("scan")}
            className={cn(
              "flex items-center gap-1.5 px-3 py-2 text-xs font-medium transition",
              mode === "scan"
                ? "bg-brand-600 text-white"
                : "text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            )}
          >
            <Scan className="w-3.5 h-3.5" />
            Scanner
          </button>
          <button
            type="button"
            onClick={() => { setMode("manual"); inputRef.current?.focus(); }}
            className={cn(
              "flex items-center gap-1.5 px-3 py-2 text-xs font-medium transition",
              mode === "manual"
                ? "bg-brand-600 text-white"
                : "text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            )}
          >
            <Search className="w-3.5 h-3.5" />
            Qo'lda
          </button>
        </div>

        {/* Input */}
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={
              mode === "scan"
                ? "Barcode skanerlang yoki shu yerga kiriting..."
                : "Barcode raqamini kiriting..."
            }
            className="w-full h-9 px-3 pr-10 rounded-lg border border-slate-200 dark:border-slate-700
              bg-slate-50 dark:bg-slate-800 text-sm text-slate-800 dark:text-white
              placeholder-slate-400 focus:outline-none focus:border-brand-500
              focus:ring-1 focus:ring-brand-500 transition"
            autoFocus={mode === "manual"}
          />
          {isLoading && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-500 animate-spin" />
          )}
        </div>

        {/* Submit */}
        {mode === "manual" && (
          <button
            type="submit"
            disabled={value.trim().length < 3 || isLoading}
            className="h-9 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white
              text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            Qo'shish
          </button>
        )}
      </form>

      {mode === "scan" && (
        <p className="mt-1.5 text-xs text-slate-400">
          Scanner ulangan bo'lsa barcode ni skanerlang — mahsulot avtomatik qo'shiladi
        </p>
      )}
    </div>
  );
}
