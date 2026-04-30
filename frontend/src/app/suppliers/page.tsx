"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, TextInput } from "@/components/ui";
import { api } from "@/lib/api";
import type { Supplier } from "@/lib/types";

export default function SuppliersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: "", contact_name: "", phone: "", email: "", gstin: "", address: "" });
  const suppliers = useQuery({ queryKey: ["suppliers"], queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data });
  const create = useMutation({
    mutationFn: async () => (await api.post<Supplier>("/suppliers", form)).data,
    onSuccess: () => {
      toast.success("Supplier saved");
      setForm({ name: "", contact_name: "", phone: "", email: "", gstin: "", address: "" });
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail ?? "Unable to save supplier")
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }
  return (
    <AppShell title="Suppliers">
      <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Supplier</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <TextInput placeholder="Contact" value={form.contact_name} onChange={(event) => setForm({ ...form, contact_name: event.target.value })} />
            <TextInput placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
            <TextInput type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <TextInput placeholder="GSTIN" value={form.gstin} onChange={(event) => setForm({ ...form, gstin: event.target.value })} />
            <Button className="w-full">Save</Button>
          </form>
        </Panel>
        <Panel>
          {(suppliers.data ?? []).length === 0 ? <EmptyState text="No suppliers" /> : (
            <table className="w-full text-sm">
              <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500"><tr><th className="py-2">Name</th><th>Contact</th><th>Phone</th><th>GSTIN</th></tr></thead>
              <tbody>{(suppliers.data ?? []).map((supplier) => <tr key={supplier.id} className="border-b border-line last:border-0"><td className="py-3 font-medium">{supplier.name}</td><td>{supplier.contact_name ?? "-"}</td><td>{supplier.phone ?? "-"}</td><td>{supplier.gstin ?? "-"}</td></tr>)}</tbody>
            </table>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
