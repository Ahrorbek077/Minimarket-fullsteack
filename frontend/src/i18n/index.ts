"use client";
import { useAuthStore } from "@/store/authStore";
import uz from "./uz.json";
import ru from "./ru.json";

const translations = { uz, uz_cryl: uz, ru, en: uz } as const;

type DeepValue<T> = T extends object
  ? { [K in keyof T]: DeepValue<T[K]> }
  : string;

export function useT() {
  const lang = useAuthStore((s) => s.user?.language ?? "uz");
  const t    = translations[lang as keyof typeof translations] ?? uz;

  function get(path: string): string {
    const keys   = path.split(".");
    let   result: any = t;
    for (const key of keys) {
      result = result?.[key];
      if (result === undefined) return path;
    }
    return typeof result === "string" ? result : path;
  }

  return get;
}
