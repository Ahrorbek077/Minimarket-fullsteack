"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  Plus, Search, Users, Shield, UserCheck, UserX,
  Pencil, Trash2, KeyRound, Loader2, RefreshCw,
} from "lucide-react";
import { staffService } from "@/services/staff.service";
import { StaffModal } from "@/components/staff/StaffModal";
import { cn } from "@/lib/utils";
import type { User, UserRole } from "@/types";

const ROLE_CONFIG: Record<string, { label: string; color: string }> = {
  super_admin: { label: "Super Admin", color: "bg-purple-100 text-purple-700 dark:bg-purple-950/40 dark:text-purple-400" },
  admin:       { label: "Admin",       color: "bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400" },
  cashier:     { label: "Kassir",      color: "bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400" },
  storekeeper: { label: "Omborchi",    color: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400" },
  accountant:  { label: "Buxgalter",   color: "bg-rose-100 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400" },
};

export default function StaffPage() {
  const qc = useQueryClient();
  const [search,     setSearch]     = useState("");
  const [page,       setPage]       = useState(1);
  const [modal,      setModal]      = useState<User | null | "new">(null);
  const [resetUser,  setResetUser]  = useState<User | null>(null);
  const [newPw,      setNewPw]      = useState("");
  const [resetting,  setResetting]  = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["staff", search, page],
    queryFn:  () => staffService.getAll({ search: search || undefined, page, page_size: 20 }),
  });

  const deleteMutation = useMutation({
    mutationFn: staffService.softDelete,
    onSuccess:  () => { qc.invalidateQueries({ queryKey: ["staff"] }); toast.success("Xodim ishdan bo'shatildi"); },
    onError:    (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  const handleResetPassword = async () => {
    if (!resetUser || !newPw || newPw.length < 8) {
      toast.error("Kamida 8 belgi bo'lishi kerak");
      return;
    }
    setResetting(true);
    try {
      await staffService.resetPassword(resetUser.id, newPw);
      toast.success("Parol tiklandi");
      setResetUser(null);
      setNewPw("");
    } catch (e: any) {
      toast.error(e?.response?.data?.error?.message || "Xato");
    } finally {
      setResetting(false);
    }
  };

  // Stats
  const total    = data?.count ?? 0;
  const active   = data?.results.filter(u => true).length ?? 0;
  const inactive = (data?.results.length ?? 0) - active;

  return (
    <div className="space-y-5">

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Users,     label: "Jami xodimlar", value: String(total),    color: "blue"   },
          { icon: UserCheck, label: "Faol",           value: String(active),   color: "green"  },
          { icon: Shield,    label: "Adminlar",       value: String(data?.results.filter(u => ["admin","super_admin"].includes(u.role)).length ?? 0), color: "purple" },
          { icon: UserX,     label: "Nofaol",         value: String(inactive), color: "red"    },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3">
            <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center shrink-0",
              color === "blue"   ? "bg-blue-50 dark:bg-blue-950/30 text-blue-600" :
              color === "green"  ? "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600" :
              color === "purple" ? "bg-purple-50 dark:bg-purple-950/30 text-purple-600" :
                                   "bg-red-50 dark:bg-red-950/30 text-red-500"
            )}>
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs text-slate-500">{label}</p>
              <p className="font-bold text-slate-800 dark:text-white">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Ism yoki email..."
            className="w-full h-9 pl-9 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />
        </div>
        <button onClick={() => setModal("new")}
          className="h-9 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white flex items-center gap-2 text-sm font-medium transition shadow-sm shadow-brand-600/20">
          <Plus className="w-4 h-4" /> Xodim qo'shish
        </button>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60">
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Xodim</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Rol</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 hidden md:table-cell">Telefon</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 hidden lg:table-cell">Qo'shilgan</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Holat</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500">Amallar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="py-12 text-center">
                  <Loader2 className="w-5 h-5 text-brand-500 animate-spin mx-auto" />
                </td>
              </tr>
            ) : data?.results.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-slate-400">
                  <Users className="w-7 h-7 mx-auto mb-2 opacity-30" />
                  Xodim topilmadi
                </td>
              </tr>
            ) : (
              data?.results.map((user) => {
                const roleConf = ROLE_CONFIG[user.role] ?? { label: user.role, color: "bg-slate-100 text-slate-600" };
                return (
                  <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition group">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-brand-600/15 flex items-center justify-center shrink-0">
                          <span className="text-xs font-bold text-brand-600">
                            {user.full_name?.[0]?.toUpperCase() ?? "U"}
                          </span>
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-slate-800 dark:text-white truncate">{user.full_name}</p>
                          <p className="text-xs text-slate-400 truncate">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn("inline-block px-2 py-0.5 rounded-full text-xs font-medium", roleConf.color)}>
                        {roleConf.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500 hidden md:table-cell">
                      {user.phone || "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400 hidden lg:table-cell">
                      {new Date(user.date_joined).toLocaleDateString("uz-UZ")}
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn(
                        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                        true
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400"
                          : "bg-red-100 text-red-600 dark:bg-red-950/40 dark:text-red-400"
                      )}>
                        <span className={cn("w-1.5 h-1.5 rounded-full", true ? "bg-emerald-500" : "bg-red-500")} />
                        {true ? "Faol" : "Nofaol"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setResetUser(user)} title="Parolni tiklash"
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition">
                          <KeyRound className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => setModal(user)} title="Tahrirlash"
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition">
                          <Pencil className="w-3.5 h-3.5" />
                        </button>
                        {user.role !== "super_admin" && (
                          <DeleteButton onConfirm={() => deleteMutation.mutate(user.id)} />
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {(data?.total_pages ?? 1) > 1 && (
          <div className="flex items-center justify-center gap-2 p-4 border-t border-slate-100 dark:border-slate-800">
            <button onClick={() => setPage(p => p - 1)} disabled={page <= 1}
              className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition">
              ← Oldingi
            </button>
            <span className="h-8 px-3 rounded-lg bg-brand-600 text-white text-sm flex items-center">{page}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= (data?.total_pages ?? 1)}
              className="h-8 px-3 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-500 hover:bg-slate-50 disabled:opacity-40 transition">
              Keyingi →
            </button>
          </div>
        )}
      </div>

      {/* Staff Modal */}
      {modal !== null && (
        <StaffModal
          user={modal === "new" ? null : modal}
          onClose={() => setModal(null)}
          onSaved={() => { qc.invalidateQueries({ queryKey: ["staff"] }); setModal(null); }}
        />
      )}

      {/* Password Reset Modal */}
      {resetUser !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => { setResetUser(null); setNewPw(""); }} />
          <div className="relative w-full max-w-sm bg-white dark:bg-slate-900 rounded-2xl shadow-2xl p-6">
            <h3 className="font-semibold text-slate-800 dark:text-white mb-1">Parolni tiklash</h3>
            <p className="text-xs text-slate-400 mb-4">{resetUser.full_name} — {resetUser.email}</p>

            <div className="flex items-center gap-2 mb-4">
              <input
                type="text"
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                placeholder="Yangi parol (8+ belgi)"
                className="flex-1 h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition"
              />
              <button type="button" onClick={() => setNewPw(Math.random().toString(36).slice(-10))}
                className="h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center gap-1.5 text-xs text-slate-500 hover:text-brand-600 hover:border-brand-400 transition shrink-0">
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex gap-3">
              <button onClick={() => { setResetUser(null); setNewPw(""); }}
                className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                Bekor
              </button>
              <button onClick={handleResetPassword} disabled={resetting || newPw.length < 8}
                className="flex-1 h-10 rounded-xl bg-amber-500 hover:bg-amber-400 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50">
                {resetting ? <><Loader2 className="w-4 h-4 animate-spin" /> Tiklanmoqda...</> : <><KeyRound className="w-4 h-4" /> Tiklash</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function DeleteButton({ onConfirm }: { onConfirm: () => void }) {
  const [confirm, setConfirm] = useState(false);
  return (
    <button
      onClick={() => confirm ? onConfirm() : setConfirm(true)}
      onBlur={() => setTimeout(() => setConfirm(false), 200)}
      title={confirm ? "Yana bosing" : "Ishdan bo'shatish"}
      className={cn(
        "w-7 h-7 rounded-lg flex items-center justify-center transition",
        confirm
          ? "bg-red-500 text-white"
          : "text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
      )}>
      <Trash2 className="w-3.5 h-3.5" />
    </button>
  );
}
