"use client";
import { useEffect, useRef, useCallback } from "react";

/**
 * USB/Bluetooth barcode scanner hook.
 * Scanner klaviatura sifatida input yuboradi — Enter bilan tugaydi.
 */
export function useBarcode(onScan: (barcode: string) => void) {
  const buffer  = useRef("");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleKeydown = useCallback((e: KeyboardEvent) => {
    // Input yoki textarea fokusida bo'lsa — skip
    const tag = (e.target as HTMLElement | null)?.tagName ?? "";
    if (tag === "INPUT" || tag === "TEXTAREA") return;

    if (e.key === "Enter") {
      if (buffer.current.length >= 3) {
        onScan(buffer.current.trim());
      }
      buffer.current = "";
      return;
    }

    if (e.key.length === 1) {
      buffer.current += e.key;
      // 100ms ichida yangi belgi kelmasa — reset
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => { buffer.current = ""; }, 100);
    }
  }, [onScan]);

  useEffect(() => {
    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  }, [handleKeydown]);
}
