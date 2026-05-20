"use client";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface Props {
  onConfirm:     () => void;
  label?:        string;
  confirmLabel?: string;
  className?:    string;
  children:      React.ReactNode;
  timeout?:      number;   // ms, default 3000
}

/**
 * Birinchi bosganda tasdiqlash so'raydi, ikkinchi bosganda bajaradi.
 * Tasodifiy o'chirish / bekor qilishdan himoya.
 */
export function ConfirmButton({
  onConfirm, label, confirmLabel = "Tasdiqlang",
  className, children, timeout = 3000,
}: Props) {
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!confirming) return;
    const t = setTimeout(() => setConfirming(false), timeout);
    return () => clearTimeout(t);
  }, [confirming, timeout]);

  const handleClick = () => {
    if (confirming) { onConfirm(); setConfirming(false); }
    else            { setConfirming(true); }
  };

  return (
    <button
      onClick={handleClick}
      title={confirming ? confirmLabel : label}
      className={cn(
        "transition",
        confirming ? "bg-red-500 text-white rounded-lg" : "",
        className
      )}
    >
      {children}
    </button>
  );
}
