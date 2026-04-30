"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, TextInput } from "@/components/ui";
import { api } from "@/lib/api";
import type { Customer } from "@/lib/types";

export default function CustomersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: "", phone: "", email: "", address: "" });
  const customers = useQuery({ queryKey: ["customers"], queryFn: async () => (await api.get<Customer[]>("/customers")).data });
  const create = useMutation({
    mutationFn: async () => (await api.post<Customer>("/customers", form)).data,
    onSuccess: () => {
      toast.success("Customer saved");
      setForm({ name: "", phone: "", email: "", address: "" });
      void queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail ?? "Unable to save customer")
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }
  return (
    <AppShell title="Customers">
      <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Customer</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <TextInput placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
            <TextInput type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <TextInput placeholder="Address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
            <Button className="w-full">Save</Button>
          </form>
        </Panel>
        <Panel>
          {(customers.data ?? []).length === 0 ? <EmptyState text="No customers" /> : (
            <table className="w-full text-sm">
              <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500"><tr><th className="py-2">Name</th><th>Phone</th><th>Email</th><th>Points</th></tr></thead>
              <tbody>{(customers.data ?? []).map((customer) => <tr key={customer.id} className="border-b border-line last:border-0"><td className="py-3 font-medium">{customer.name}</td><td>{customer.phone ?? "-"}</td><td>{customer.email ?? "-"}</td><td>{customer.loyalty_points}</td></tr>)}</tbody>
            </table>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
