"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import type { Supplier } from "@/lib/types";

const blank = { name: "", contact_name: "", phone: "", email: "", gstin: "", address: "", payment_terms: "Net 7", credit_days: "7" };

export default function SuppliersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(blank);
  const suppliers = useQuery({ queryKey: ["suppliers"], queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data });
  const create = useMutation({
    mutationFn: async () => (await api.post<Supplier>("/suppliers", { ...form, credit_days: Number(form.credit_days || 0) })).data,
    onSuccess: () => {
      toast.success("Supplier saved");
      setForm(blank);
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to save supplier"))
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }
  return (
    <AppShell title="Suppliers">
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Supplier</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <div className="grid grid-cols-2 gap-2">
              <TextInput placeholder="Contact" value={form.contact_name} onChange={(event) => setForm({ ...form, contact_name: event.target.value })} />
              <TextInput placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
            </div>
            <TextInput type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <TextInput placeholder="GSTIN" value={form.gstin} onChange={(event) => setForm({ ...form, gstin: event.target.value })} />
            <div className="grid grid-cols-2 gap-2">
              <TextInput placeholder="Payment terms" value={form.payment_terms} onChange={(event) => setForm({ ...form, payment_terms: event.target.value })} />
              <TextInput type="number" min={0} placeholder="Credit days" value={form.credit_days} onChange={(event) => setForm({ ...form, credit_days: event.target.value })} />
            </div>
            <TextInput placeholder="Address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
            <Button disabled={create.isPending} className="w-full">Save</Button>
          </form>
        </Panel>
        <Panel>
          {(suppliers.data ?? []).length === 0 ? <EmptyState text="No suppliers" /> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[780px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500"><tr><th className="py-2">Name</th><th>Contact</th><th>GSTIN</th><th>Terms</th><th>Credit</th></tr></thead>
                <tbody>{(suppliers.data ?? []).map((supplier) => <tr key={supplier.id} className="border-b border-line last:border-0"><td className="py-3"><div className="font-medium">{supplier.name}</div><div className="text-xs text-gray-500">{supplier.email ?? "-"}</div></td><td>{supplier.contact_name ?? "-"}<div className="text-xs text-gray-500">{supplier.phone ?? "-"}</div></td><td>{supplier.gstin ?? "-"}</td><td>{supplier.payment_terms ?? "-"}</td><td>{supplier.credit_days} days</td></tr>)}</tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
