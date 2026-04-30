"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import type { Role, User } from "@/lib/types";

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "CASHIER" as Role });
  const users = useQuery({ queryKey: ["users"], queryFn: async () => (await api.get<User[]>("/users")).data });
  const create = useMutation({
    mutationFn: async () => (await api.post<User>("/users", form)).data,
    onSuccess: () => {
      toast.success("User saved");
      setForm({ full_name: "", email: "", password: "", role: "CASHIER" });
      void queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to save user"))
  });
  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }
  return (
    <AppShell title="Users">
      <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New User</h2>
            <TextInput required placeholder="Full name" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} />
            <TextInput required type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <TextInput required type="password" minLength={8} placeholder="Password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />
            <Select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as Role })}>
              <option value="CASHIER">Cashier</option>
              <option value="ADMIN">Admin</option>
            </Select>
            <Button className="w-full">Save</Button>
          </form>
        </Panel>
        <Panel>
          {users.isLoading ? (
            <EmptyState text="Loading users" />
          ) : users.isError ? (
            <EmptyState text={apiErrorMessage(users.error, "Unable to load users")} />
          ) : (users.data ?? []).length === 0 ? <EmptyState text="No users" /> : (
            <table className="w-full text-sm">
              <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500"><tr><th className="py-2">Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
              <tbody>{(users.data ?? []).map((user) => <tr key={user.id} className="border-b border-line last:border-0"><td className="py-3 font-medium">{user.full_name}</td><td>{user.email}</td><td>{user.role}</td><td>{user.is_active ? "Active" : "Inactive"}</td></tr>)}</tbody>
            </table>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
