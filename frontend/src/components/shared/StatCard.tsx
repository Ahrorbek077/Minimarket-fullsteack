import { cn } from "@/lib/utils";

interface StatCardProps {
  icon:      React.ElementType;
  label:     string;
  value:     string | number;
  color:     "blue" | "amber" | "red" | "green" | "emerald" | "violet";
  className?: string;
}

const COLOR_MAP: Record<StatCardProps["color"], string> = {
  blue:    "bg-blue-50 dark:bg-blue-950/30 text-blue-600",
  amber:   "bg-amber-50 dark:bg-amber-950/30 text-amber-600",
  red:     "bg-red-50 dark:bg-red-950/30 text-red-500",
  green:   "bg-green-50 dark:bg-green-950/30 text-green-600",
  emerald: "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600",
  violet:  "bg-violet-50 dark:bg-violet-950/30 text-violet-600",
};

export function StatCard({ icon: Icon, label, value, color, className }: StatCardProps) {
  return (
    <div className={cn(
      "bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3",
      className
    )}>
      <div className={cn(
        "w-9 h-9 rounded-lg flex items-center justify-center shrink-0",
        COLOR_MAP[color]
      )}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-slate-500 truncate">{label}</p>
        <p className="font-bold text-slate-800 dark:text-white truncate">{value}</p>
      </div>
    </div>
  );
}
