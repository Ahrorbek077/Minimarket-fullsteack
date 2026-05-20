"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, ShoppingCart, Package, ShoppingBag,
  Building2, Warehouse, Receipt, History, BarChart3,
  Settings, Store, ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useT } from "@/i18n";

const navItems = [
  { href: "/",           icon: LayoutDashboard, key: "dashboard",  roles: ["all"] },
  { href: "/pos",        icon: ShoppingCart,    key: "pos",        roles: ["all"] },
  { href: "/products",   icon: Package,         key: "products",   roles: ["all"] },
  { href: "/purchases",  icon: ShoppingBag,     key: "purchases",  roles: ["admin","super_admin","storekeeper"] },
  { href: "/companies",  icon: Building2,       key: "companies",  roles: ["admin","super_admin"] },
  { href: "/inventory",  icon: Warehouse,       key: "inventory",  roles: ["admin","super_admin","storekeeper"] },
  { href: "/sales",      icon: Receipt,         key: "sales",      roles: ["all"] },
  { href: "/history",    icon: History,         key: "history",    roles: ["admin","super_admin","accountant"] },
  { href: "/reports",    icon: BarChart3,       key: "reports",    roles: ["admin","super_admin","accountant"] },
  { href: "/settings",   icon: Settings,        key: "settings",   roles: ["all"] },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user }  = useAuth();
  const t         = useT();

  const visible = navItems.filter((item) =>
    item.roles.includes("all") || item.roles.includes(user?.role ?? "")
  );

  return (
    <aside className="w-60 shrink-0 h-full bg-slate-900 dark:bg-slate-950 border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="h-15 flex items-center gap-3 px-5 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
          <Store className="w-4 h-4 text-white" />
        </div>
        <span className="font-semibold text-white text-sm">Mini Market</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-0.5">
        {visible.map(({ href, icon: Icon, key }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all group",
                active
                  ? "bg-brand-600/15 text-brand-400 font-medium"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
              )}
            >
              <Icon className={cn("w-4 h-4 shrink-0", active && "text-brand-400")} />
              <span className="flex-1">{t(`nav.${key}`)}</span>
              {active && <ChevronRight className="w-3 h-3 text-brand-400" />}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="p-3 border-t border-slate-800">
        <div className="flex items-center gap-3 px-2 py-1.5">
          <div className="w-7 h-7 rounded-full bg-brand-600/20 flex items-center justify-center shrink-0">
            <span className="text-xs font-bold text-brand-400">
              {user?.full_name?.[0]?.toUpperCase() ?? "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-500 capitalize truncate">{user?.role_display}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
