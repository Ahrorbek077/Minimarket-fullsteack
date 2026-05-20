"use client";
import { usePathname, useRouter } from "next/navigation";
import { Moon, Sun, Monitor, LogOut, Bell } from "lucide-react";
import { useTheme } from "next-themes";
import { toast } from "react-hot-toast";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/auth.service";
import { useT } from "@/i18n";
import { cn } from "@/lib/utils";

const pageTitles: Record<string, string> = {
  "/":           "dashboard", "/pos":       "pos",
  "/products":   "products",  "/purchases": "purchases",
  "/companies":  "companies", "/inventory": "inventory",
  "/sales":      "sales",     "/history":   "history",
  "/reports":    "reports",   "/settings":  "settings",
};

export function Header() {
  const pathname    = usePathname();
  const router      = useRouter();
  const { theme, setTheme } = useTheme();
  const { refreshToken, logout } = useAuthStore();
  const t = useT();

  const titleKey = Object.keys(pageTitles)
    .reverse()
    .find((k) => pathname === k || pathname.startsWith(k + "/")) ?? "/";
  const title = t(`nav.${pageTitles[titleKey] ?? "dashboard"}`);

  const cycleTheme = () => {
    setTheme(theme === "light" ? "dark" : theme === "dark" ? "system" : "light");
  };

  const handleLogout = async () => {
    try {
      if (refreshToken) await authService.logout(refreshToken);
    } catch {}
    logout();
    router.push("/login");
    toast.success("Tizimdan chiqildi");
  };

  const ThemeIcon = theme === "light" ? Sun : theme === "dark" ? Moon : Monitor;

  return (
    <header className="h-15 shrink-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6">
      <h1 className="font-semibold text-slate-800 dark:text-white text-base">{title}</h1>

      <div className="flex items-center gap-1">
        {/* Theme toggle */}
        <button
          onClick={cycleTheme}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          title="Mavzuni almashtirish"
        >
          <ThemeIcon className="w-4 h-4" />
        </button>

        {/* Notifications */}
        <button className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
          <Bell className="w-4 h-4" />
        </button>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition"
          title="Chiqish"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
