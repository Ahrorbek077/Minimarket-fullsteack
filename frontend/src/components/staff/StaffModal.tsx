"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import { X, Loader2, Eye, EyeOff, User } from "lucide-react";
import { staffService } from "@/services/staff.service";
import { cn } from "@/lib/utils";
import type { User as UserType, UserRole } from "@/types";

const ROLES: { value: UserRole; label: string; desc: string }[] = [
  { value: "admin",       label: "Admin",      desc: "Barcha sahifalarni boshqaradi" },
  { value: "cashier",     label: "Kassir",     desc: "Kassa va sotuvlar" },
  { value: "storekeeper", label: "Omborchi",   desc: "Ombor va xaridlar" },
  { value: "accountant",  label: "Buxgalter",  desc: "Hisobotlar va tarix" },
];

const createSchema = z.object({
  full_name: z.string().min(2, "Kamida 2 belgi"),
  email:     z.string().email("Email noto'g'ri"),
  phone:     z.string().optional(),
  role:      z.string().min(1, "Rol tanlang"),
  password:  z.string().min(8, "Kamida 8 belgi"),
});

const editSchema = z.object({
  full_name: z.string().min(2, "Kamida 2 belgi"),
  phone:     z.string().optional(),
  role:      z.string().min(1, "Rol tanlang"),
});

type CreateForm = z.infer<typeof createSchema>;
type EditForm   = z.infer<typeof editSchema>;

interface Props {
  user:    UserType | null;
  onClose: () => void;
  onSaved: () => void;
}

export function StaffModal({ user, onClose, onSaved }: Props) {
  const isEdit  = !!user;
  const [saving, setSaving]   = useState(false);
  const [showPw, setShowPw]   = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<any>({
    resolver: zodResolver(isEdit ? editSchema : createSchema),
    defaultValues: isEdit
      ? { full_name: user.full_name, phone: user.phone, role: user.role }
      : { role: "cashier" },
  });

  const selectedRole = watch("role");

  const onSubmit = async (data: any) => {
    setSaving(true);
    try {
      if (isEdit) {
        await staffService.update(user!.id, { full_name: data.full_name, phone: data.phone, role: data.role });
        toast.success("Xodim yangilandi");
      } else {
        await staffService.create({ ...data });
        toast.success("Xodim qo'shildi");
      }
      onSaved();
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || err?.response?.data?.email?.[0] || "Xato yuz berdi";
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-600/10 flex items-center justify-center">
              <User className="w-4 h-4 text-brand-600" />
            </div>
            <h2 className="font-semibold text-slate-800 dark:text-white">
              {isEdit ? "Xodimni tahrirlash" : "Yangi xodim"}
            </h2>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">

            {/* Full name */}
            <Field label="To'liq ism *" error={errors.full_name?.message as string}>
              <input {...register("full_name")} placeholder="Ism Familiya" className={inputCls(!!errors.full_name)} />
            </Field>

            {/* Email — only on create */}
            {!isEdit && (
              <Field label="Email *" error={errors.email?.message as string}>
                <input {...register("email")} type="email" placeholder="xodim@email.com" className={inputCls(!!errors.email)} />
              </Field>
            )}
            {isEdit && (
              <div className="px-3 py-2 rounded-lg bg-slate-50 dark:bg-slate-800 text-sm text-slate-500">
                📧 {user?.email}
              </div>
            )}

            {/* Phone */}
            <Field label="Telefon">
              <input {...register("phone")} placeholder="+998 90 123 45 67" className={inputCls(false)} />
            </Field>

            {/* Role */}
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-2">Rol *</label>
              <div className="grid grid-cols-2 gap-2">
                {ROLES.map(({ value, label, desc }) => (
                  <label key={value}
                    className={cn(
                      "relative flex flex-col gap-0.5 px-3 py-2.5 rounded-xl border-2 cursor-pointer transition",
                      selectedRole === value
                        ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
                        : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                    )}>
                    <input {...register("role")} type="radio" value={value} className="sr-only" />
                    <span className={cn("text-xs font-semibold", selectedRole === value ? "text-brand-700 dark:text-brand-400" : "text-slate-700 dark:text-slate-200")}>
                      {label}
                    </span>
                    <span className="text-xs text-slate-400">{desc}</span>
                  </label>
                ))}
              </div>
              {errors.role && <p className="mt-1 text-xs text-red-400">{errors.role.message as string}</p>}
            </div>

            {/* Password — only on create */}
            {!isEdit && (
              <Field label="Parol *" error={errors.password?.message as string}>
                <div className="relative">
                  <input {...register("password")} type={showPw ? "text" : "password"} placeholder="Kamida 8 belgi" className={cn(inputCls(!!errors.password), "pr-10")} />
                  <button type="button" onClick={() => setShowPw(p => !p)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition">
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </Field>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex gap-3">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button type="submit" disabled={saving}
              className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-60 shadow-sm shadow-brand-600/20">
              {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saqlanmoqda...</> : isEdit ? "Saqlash" : "Qo'shish"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-500 mb-1.5">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  );
}

function inputCls(hasError: boolean) {
  return cn(
    "w-full h-9 px-3 rounded-lg border text-sm focus:outline-none focus:ring-1 transition",
    "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
    hasError
      ? "border-red-400 focus:border-red-400 focus:ring-red-400"
      : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
  );
}
