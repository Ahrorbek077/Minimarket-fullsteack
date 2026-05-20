"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import { X, Loader2, Building2, Check } from "lucide-react";
import { companyService } from "@/services/company.service";
import { cn } from "@/lib/utils";
import type { Company } from "@/types";

const schema = z.object({
  name:    z.string().min(2, "Kamida 2 belgi"),
  phone:   z.string().optional(),
  address: z.string().optional(),
  inn:     z.string().optional(),
  note:    z.string().optional(),
});
type FormData = z.infer<typeof schema>;

interface Props {
  company: Company | null;
  onClose: () => void;
  onSaved: () => void;
}

export function CompanyModal({ company, onClose, onSaved }: Props) {
  const isEdit = !!company;
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, formState: { errors, isDirty } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name:    company?.name    ?? "",
      phone:   company?.phone   ?? "",
      address: company?.address ?? "",
      inn:     company?.inn     ?? "",
    },
  });

  const onSubmit = async (data: FormData) => {
    setSaving(true);
    try {
      if (isEdit) await companyService.update(company.id, data);
      else        await companyService.create(data);
      toast.success(isEdit ? "Kompaniya yangilandi" : "Kompaniya qo'shildi");
      onSaved();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato yuz berdi");
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
            <Building2 className="w-4 h-4 text-brand-500" />
            <h2 className="font-semibold text-slate-800 dark:text-white">
              {isEdit ? "Kompaniyani tahrirlash" : "Yangi kompaniya"}
            </h2>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">

          {/* Name */}
          <Field label="Kompaniya nomi *" error={errors.name?.message}>
            <input {...register("name")} placeholder="Kompaniya LLC"
              className={fieldCls(!!errors.name)} autoFocus />
          </Field>

          {/* INN */}
          <Field label="INN (soliq raqami)">
            <input {...register("inn")} placeholder="123456789"
              className={fieldCls(false)} />
          </Field>

          {/* Phone */}
          <Field label="Telefon">
            <input {...register("phone")} placeholder="+998 71 123 45 67"
              className={fieldCls(false)} />
          </Field>

          {/* Address */}
          <Field label="Manzil">
            <textarea {...register("address")} rows={2} placeholder="Shahar, ko'cha, uy raqami..."
              className={cn(fieldCls(false), "resize-none py-2")} />
          </Field>

          {/* Note */}
          <Field label="Izoh">
            <textarea {...register("note")} rows={2} placeholder="Qo'shimcha ma'lumot..."
              className={cn(fieldCls(false), "resize-none py-2")} />
          </Field>

          {/* Footer */}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 h-10 rounded-xl border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition">
              Bekor qilish
            </button>
            <button type="submit" disabled={saving || (isEdit && !isDirty)}
              className="flex-1 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50 shadow-sm shadow-brand-600/20">
              {saving
                ? <><Loader2 className="w-4 h-4 animate-spin" />Saqlanmoqda...</>
                : <><Check className="w-4 h-4" />{isEdit ? "Saqlash" : "Qo'shish"}</>
              }
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

function fieldCls(hasError: boolean) {
  return cn(
    "w-full h-10 px-4 rounded-xl border text-sm transition focus:outline-none focus:ring-1",
    "bg-white dark:bg-slate-800 text-slate-800 dark:text-white placeholder-slate-400",
    hasError
      ? "border-red-400 focus:border-red-400 focus:ring-red-400"
      : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
  );
}
