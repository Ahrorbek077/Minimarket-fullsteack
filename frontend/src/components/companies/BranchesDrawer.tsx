"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "react-hot-toast";
import {
  X, Plus, Pencil, Trash2, GitBranch,
  Loader2, Check, ChevronDown, ChevronUp,
} from "lucide-react";
import { companyService } from "@/services/company.service";
import { cn } from "@/lib/utils";
import type { Branch, Company } from "@/types";

const branchSchema = z.object({
  name:    z.string().min(2, "Kamida 2 belgi"),
  phone:   z.string().optional(),
  address: z.string().optional(),
});
type BranchForm = z.infer<typeof branchSchema>;

interface Props {
  company: Company;
  onClose: () => void;
}

export function BranchesDrawer({ company, onClose }: Props) {
  const qc = useQueryClient();
  const [editBranch, setEditBranch] = useState<Branch | null | "new">(null);

  const { data: branches, isLoading } = useQuery({
    queryKey: ["branches", company.id],
    queryFn:  () => companyService.getBranches(company.id),
  });

  const deleteMutation = useMutation({
    mutationFn: (branchId: number) => companyService.deleteBranch(company.id, branchId),
    onSuccess:  () => { qc.invalidateQueries({ queryKey: ["branches", company.id] }); toast.success("Filial o'chirildi"); },
    onError:    (e: any) => toast.error(e?.response?.data?.error?.message || "Xato"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      {/* Drawer */}
      <div className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-brand-500" />
              <h2 className="font-semibold text-slate-800 dark:text-white">Filiallar</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{company.name}</p>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3">

          {/* Add new form */}
          {editBranch === "new" ? (
            <BranchForm
              companyId={company.id}
              branch={null}
              onClose={() => setEditBranch(null)}
              onSaved={() => { qc.invalidateQueries({ queryKey: ["branches", company.id] }); setEditBranch(null); }}
            />
          ) : (
            <button onClick={() => setEditBranch("new")}
              className="w-full flex items-center gap-2 h-10 px-4 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 text-sm text-slate-400 hover:border-brand-400 hover:text-brand-500 transition">
              <Plus className="w-4 h-4" />
              Yangi filial qo'shish
            </button>
          )}

          {/* Branches list */}
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />
            </div>
          ) : branches?.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-slate-400">
              <GitBranch className="w-7 h-7 mb-2 opacity-30" />
              <p className="text-sm">Hali filial yo'q</p>
            </div>
          ) : (
            branches?.map((branch) => (
              editBranch && (editBranch as Branch).id === branch.id ? (
                <BranchForm
                  key={branch.id}
                  companyId={company.id}
                  branch={branch}
                  onClose={() => setEditBranch(null)}
                  onSaved={() => { qc.invalidateQueries({ queryKey: ["branches", company.id] }); setEditBranch(null); }}
                />
              ) : (
                <BranchCard
                  key={branch.id}
                  branch={branch}
                  onEdit={() => setEditBranch(branch)}
                  onDelete={() => deleteMutation.mutate(branch.id)}
                />
              )
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function BranchCard({ branch, onEdit, onDelete }: {
  branch:   Branch;
  onEdit:   () => void;
  onDelete: () => void;
}) {
  const [confirmDel, setConfirmDel] = useState(false);

  return (
    <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 flex items-start justify-between group">
      <div className="min-w-0">
        <p className="font-medium text-slate-800 dark:text-white text-sm">{branch.name}</p>
        {branch.phone   && <p className="text-xs text-slate-400 mt-0.5">{branch.phone}</p>}
        {branch.address && <p className="text-xs text-slate-400 truncate">{branch.address}</p>}
      </div>
      <div className="flex gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={onEdit}
          className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-brand-500 hover:bg-white dark:hover:bg-slate-700 transition">
          <Pencil className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => confirmDel ? onDelete() : setConfirmDel(true)}
          className={cn(
            "w-7 h-7 rounded-lg flex items-center justify-center transition",
            confirmDel
              ? "bg-red-500 text-white"
              : "text-slate-400 hover:text-red-500 hover:bg-white dark:hover:bg-slate-700"
          )}
          title={confirmDel ? "Yana bosing" : "O'chirish"}>
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

function BranchForm({ companyId, branch, onClose, onSaved }: {
  companyId: number;
  branch:    Branch | null;
  onClose:   () => void;
  onSaved:   () => void;
}) {
  const isEdit = !!branch;
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<BranchForm>({
    resolver: zodResolver(branchSchema),
    defaultValues: {
      name:    branch?.name    ?? "",
      phone:   branch?.phone   ?? "",
      address: branch?.address ?? "",
    },
  });

  const onSubmit = async (data: BranchForm) => {
    setSaving(true);
    try {
      if (isEdit) await companyService.updateBranch(companyId, branch!.id, data);
      else        await companyService.createBranch(companyId, data);
      toast.success(isEdit ? "Filial yangilandi" : "Filial qo'shildi");
      onSaved();
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || "Xato");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-brand-50 dark:bg-brand-950/20 border border-brand-200 dark:border-brand-800 rounded-xl p-4 space-y-3">
      <p className="text-xs font-semibold text-brand-700 dark:text-brand-400">
        {isEdit ? "Filialni tahrirlash" : "Yangi filial"}
      </p>

      <div>
        <input {...register("name")} placeholder="Filial nomi *"
          className={cn(
            "w-full h-9 px-3 rounded-lg border text-sm focus:outline-none focus:ring-1 transition bg-white dark:bg-slate-800",
            errors.name
              ? "border-red-400 focus:ring-red-400"
              : "border-slate-200 dark:border-slate-700 focus:border-brand-500 focus:ring-brand-500"
          )}
          autoFocus
        />
        {errors.name && <p className="mt-1 text-xs text-red-400">{errors.name.message}</p>}
      </div>

      <input {...register("phone")} placeholder="Telefon"
        className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />

      <input {...register("address")} placeholder="Manzil"
        className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:border-brand-500 transition" />

      <div className="flex gap-2 pt-1">
        <button type="button" onClick={onClose}
          className="flex-1 h-8 rounded-lg border border-slate-200 dark:border-slate-700 text-xs text-slate-500 hover:bg-white dark:hover:bg-slate-800 transition">
          Bekor
        </button>
        <button
          type="button"
          onClick={handleSubmit(onSubmit)}
          disabled={saving}
          className="flex-1 h-8 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium flex items-center justify-center gap-1.5 transition disabled:opacity-50">
          {saving
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <><Check className="w-3.5 h-3.5" />{isEdit ? "Saqlash" : "Qo'shish"}</>
          }
        </button>
      </div>
    </div>
  );
}
