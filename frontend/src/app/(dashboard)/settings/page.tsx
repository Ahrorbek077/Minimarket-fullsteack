"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import { useTheme } from "next-themes";
import { User, Lock, Globe, Sun, Moon, Monitor, Check, Loader2, Eye, EyeOff, Shield } from "lucide-react";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";
import type { UserLanguage } from "@/types";

const profileSchema = z.object({
  full_name: z.string().min(2, "Kamida 2 belgi"),
  phone:     z.string().optional(),
});
type ProfileForm = z.infer<typeof profileSchema>;

const passwordSchema = z.object({
  old_password:         z.string().min(6, "Kamida 6 belgi"),
  new_password:         z.string().min(8, "Kamida 8 belgi")
    .regex(/[A-Z]/, "Katta harf bo'lishi kerak")
    .regex(/[0-9]/, "Raqam bo'lishi kerak"),
  new_password_confirm: z.string(),
}).refine((d) => d.new_password === d.new_password_confirm, {
  message: "Parollar mos emas", path: ["new_password_confirm"],
});
type PasswordForm = z.infer<typeof passwordSchema>;

const LANGUAGES: { value: UserLanguage; label: string; native: string }[] = [
  { value: "uz",      label: "O'zbek (lotin)",  native: "O'zbekcha"  },
  { value: "uz_cryl", label: "Ўзбек (кирилл)",  native: "Ўзбекча"   },
  { value: "ru",      label: "Русский",          native: "Русский"    },
];

export default function SettingsPage() {
  const [tab, setTab] = useState<"profile" | "password" | "appearance">("profile");

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      {/* Tabs */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-1.5 flex gap-1">
        {([
          { id: "profile"    as const, label: "Profil",    Icon: User  },
          { id: "password"   as const, label: "Parol",     Icon: Lock  },
          { id: "appearance" as const, label: "Ko'rinish", Icon: Globe },
        ] as const).map(({ id, label, Icon }) => (
          <button key={id} onClick={() => setTab(id)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition",
              tab === id
                ? "bg-brand-600 text-white shadow-sm"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
            )}>
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {tab === "profile"    && <ProfileSection />}
      {tab === "password"   && <PasswordSection />}
      {tab === "appearance" && <AppearanceSection />}
    </div>
  );
}

function ProfileSection() {
  const { user, setUser } = useAuthStore();
  const { register, handleSubmit, formState: { errors, isSubmitting, isDirty } } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: { full_name: user?.full_name ?? "", phone: user?.phone ?? "" },
  });

  const onSubmit = async (data: ProfileForm) => {
    try {
      const updated = await authService.updateProfile(data);
      setUser(updated);
      toast.success("Profil yangilandi");
    } catch { toast.error("Xato yuz berdi"); }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h3 className="font-semibold text-slate-800 dark:text-white">Profil ma'lumotlari</h3>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">
        {/* Avatar */}
        <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
          <div className="w-14 h-14 rounded-2xl bg-brand-600/15 flex items-center justify-center text-xl font-bold text-brand-600 shrink-0">
            {user?.full_name?.[0]?.toUpperCase() ?? "U"}
          </div>
          <div>
            <p className="font-semibold text-slate-800 dark:text-white">{user?.full_name}</p>
            <p className="text-sm text-slate-400">{user?.email}</p>
            <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium bg-brand-100 dark:bg-brand-950/40 text-brand-700 dark:text-brand-400">
              {user?.role_display}
            </span>
          </div>
        </div>

        <FField label="To'liq ism *" error={errors.full_name?.message}>
          <input {...register("full_name")} placeholder="Ism Familiya" className={fCls(!!errors.full_name)} />
        </FField>
        <FField label="Telefon" error={errors.phone?.message}>
          <input {...register("phone")} placeholder="+998 90 123 45 67" className={fCls(!!errors.phone)} />
        </FField>

        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Email",      value: user?.email        ?? "—" },
            { label: "Qo'shilgan", value: user?.date_joined?.slice(0, 10) ?? "—" },
          ].map(({ label, value }) => (
            <div key={label} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
              <p className="text-xs text-slate-400 mb-0.5">{label}</p>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{value}</p>
            </div>
          ))}
        </div>

        <button type="submit" disabled={isSubmitting || !isDirty}
          className="w-full h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-brand-600/20">
          {isSubmitting ? <><Loader2 className="w-4 h-4 animate-spin" />Saqlanmoqda...</> : <><Check className="w-4 h-4" />Saqlash</>}
        </button>
      </form>
    </div>
  );
}

function PasswordSection() {
  const [show, setShow] = useState({ old: false, new: false, confirm: false });
  const toggle = (k: keyof typeof show) => setShow(p => ({ ...p, [k]: !p[k] }));

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmit = async (data: PasswordForm) => {
    try {
      await authService.changePassword(data.old_password, data.new_password, data.new_password_confirm);
      toast.success("Parol muvaffaqiyatli o'zgartirildi");
      reset();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato yuz berdi");
    }
  };

  const FIELDS = [
    { k: "old"    as const, label: "Eski parol",              field: "old_password"         as const, ph: "Joriy parol"           },
    { k: "new"    as const, label: "Yangi parol",             field: "new_password"         as const, ph: "Yangi parol (8+ belgi)" },
    { k: "confirm"as const, label: "Yangi parolni tasdiqlang",field: "new_password_confirm" as const, ph: "Qaytaring"              },
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h3 className="font-semibold text-slate-800 dark:text-white">Parolni almashtirish</h3>
        <p className="text-xs text-slate-400 mt-0.5">Avval joriy parolni kiriting</p>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
        {FIELDS.map(({ k, label, field, ph }) => (
          <FField key={k} label={label} error={errors[field]?.message}>
            <div className="relative">
              <input {...register(field)} type={show[k] ? "text" : "password"} placeholder={ph}
                className={cn(fCls(!!errors[field]), "pr-10")} />
              <button type="button" onClick={() => toggle(k)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition">
                {show[k] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </FField>
        ))}

        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 space-y-1.5">
          <p className="text-xs font-medium text-slate-500">Parol talablari:</p>
          {["Kamida 8 belgi", "Kamida 1 katta harf (A-Z)", "Kamida 1 raqam (0-9)"].map(r => (
            <p key={r} className="flex items-center gap-1.5 text-xs text-slate-400">
              <Shield className="w-3 h-3 shrink-0" />{r}
            </p>
          ))}
        </div>

        <button type="submit" disabled={isSubmitting}
          className="w-full h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-brand-600/20">
          {isSubmitting ? <><Loader2 className="w-4 h-4 animate-spin" />O'zgartirilmoqda...</> : <><Lock className="w-4 h-4" />Parolni o'zgartirish</>}
        </button>
      </form>
    </div>
  );
}

function AppearanceSection() {
  const { theme, setTheme }         = useTheme();
  const { user, setUser }           = useAuthStore();
  const [langSaving, setLangSaving] = useState(false);

  const handleLang = async (lang: UserLanguage) => {
    setLangSaving(true);
    try {
      const updated = await authService.updateProfile({ language: lang });
      setUser(updated);
      toast.success("Til o'zgartirildi");
    } catch { toast.error("Xato yuz berdi"); }
    finally { setLangSaving(false); }
  };

  return (
    <div className="space-y-4">
      {/* Theme */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h3 className="font-semibold text-slate-800 dark:text-white">Mavzu</h3>
        </div>
        <div className="p-6 grid grid-cols-3 gap-3">
          {([
            { v: "light",  l: "Kunduzgi", I: Sun     },
            { v: "dark",   l: "Tungi",    I: Moon    },
            { v: "system", l: "Tizim",    I: Monitor },
          ] as const).map(({ v, l, I }) => (
            <button key={v} onClick={() => setTheme(v)}
              className={cn(
                "relative flex flex-col items-center gap-2.5 p-4 rounded-xl border-2 transition",
                theme === v
                  ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              )}>
              <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center",
                theme === v ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-500")}>
                <I className="w-5 h-5" />
              </div>
              <span className={cn("text-xs font-medium",
                theme === v ? "text-brand-700 dark:text-brand-400" : "text-slate-600 dark:text-slate-400")}>
                {l}
              </span>
              {theme === v && <Check className="absolute top-2 right-2 w-3.5 h-3.5 text-brand-600" />}
            </button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h3 className="font-semibold text-slate-800 dark:text-white">Interfeys tili</h3>
        </div>
        <div className="p-4 space-y-2">
          {LANGUAGES.map(({ value, label, native }) => {
            const active = user?.language === value;
            return (
              <button key={value} onClick={() => handleLang(value)} disabled={langSaving}
                className={cn(
                  "w-full flex items-center gap-4 px-4 py-3 rounded-xl border-2 transition text-left",
                  active
                    ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
                    : "border-transparent hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-200 dark:hover:border-slate-700"
                )}>
                <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0",
                  active ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-500")}>
                  {value === "ru" ? "Ru" : "Uz"}
                </div>
                <div className="flex-1">
                  <p className={cn("text-sm font-medium", active ? "text-brand-700 dark:text-brand-400" : "text-slate-700 dark:text-slate-300")}>{label}</p>
                  <p className="text-xs text-slate-400">{native}</p>
                </div>
                {active && (langSaving
                  ? <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />
                  : <Check   className="w-4 h-4 text-brand-600" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function FField({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-500 mb-1.5">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-red-400">{error}</p>}
    </div>
  );
}

function fCls(err: boolean) {
  return cn(
    "w-full h-10 px-4 rounded-xl border text-sm transition focus:outline-none focus:ring-1",
    "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
    err
      ? "border-red-400 focus:border-red-400 focus:ring-red-400"
      : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
  );
}
