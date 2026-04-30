"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import type { Customer } from "@/lib/types";

const blank = { name: "", phone: "", email: "", address: "", loyalty_tier: "REGULAR", credit_limit: "0" };

export default function CustomersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(blank);
  const customers = useQuery({ queryKey: ["customers"], queryFn: async () => (await api.get<Customer[]>("/customers")).data });
  const create = useMutation({
    mutationFn: async () => (await api.post<Customer>("/customers", { ...form, phone: form.phone || null, email: form.email || null, credit_limit: Number(form.credit_limit || 0) })).data,
    onSuccess: () => {
      toast.success("Customer saved");
      setForm(blank);
      void queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to save customer"))
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }
  return (
    <AppShell title="Customers">
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Customer</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <div className="grid grid-cols-2 gap-2">
              <TextInput placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
              <TextInput type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Select value={form.loyalty_tier} onChange={(event) => setForm({ ...form, loyalty_tier: event.target.value })}>
                <option value="REGULAR">Regular</option>
                <option value="SILVER">Silver</option>
                <option value="GOLD">Gold</option>
                <option value="PLATINUM">Platinum</option>
              </Select>
              <TextInput type="number" min={0} step="0.01" placeholder="Credit limit" value={form.credit_limit} onChange={(event) => setForm({ ...form, credit_limit: event.target.value })} />
            </div>
            <TextInput placeholder="Address" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
            <Button disabled={create.isPending} className="w-full">Save</Button>
          </form>
        </Panel>
        <Panel>
          {(customers.data ?? []).length === 0 ? <EmptyState text="No customers" /> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500"><tr><th className="py-2">Name</th><th>Phone</th><th>Tier</th><th>Points</th><th>Credit</th></tr></thead>
                <tbody>{(customers.data ?? []).map((customer) => <tr key={customer.id} className="border-b border-line last:border-0"><td className="py-3"><div className="font-medium">{customer.name}</div><div className="text-xs text-gray-500">{customer.email ?? "-"}</div></td><td>{customer.phone ?? "-"}</td><td>{customer.loyalty_tier}</td><td>{customer.loyalty_points}</td><td>{money(customer.credit_limit)}</td></tr>)}</tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
