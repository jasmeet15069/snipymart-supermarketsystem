"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api } from "@/lib/api";
import { money } from "@/lib/format";
import type { Category, Product } from "@/lib/types";

const blank = {
  name: "",
  sku: "",
  barcode: "",
  category_id: "",
  selling_price: "",
  cost_price: "",
  gst_rate: "5",
  unit: "pcs",
  reorder_level: "5",
  opening_quantity: "0",
  opening_batch_number: "OPENING"
};

export default function ProductsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(blank);
  const [search, setSearch] = useState("");
  const products = useQuery({
    queryKey: ["products", search],
    queryFn: async () => (await api.get<Product[]>("/products", { params: { search: search || undefined } })).data
  });
  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data
  });
  const create = useMutation({
    mutationFn: async () => {
      const payload = {
        ...form,
        category_id: form.category_id ? Number(form.category_id) : null,
        selling_price: Number(form.selling_price),
        cost_price: Number(form.cost_price),
        gst_rate: Number(form.gst_rate),
        reorder_level: Number(form.reorder_level),
        opening_quantity: Number(form.opening_quantity)
      };
      return (await api.post<Product>("/products", payload)).data;
    },
    onSuccess: () => {
      toast.success("Product saved");
      setForm(blank);
      void queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail ?? "Unable to save product")
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }

  return (
    <AppShell title="Products">
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Product</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <div className="grid grid-cols-2 gap-2">
              <TextInput required placeholder="SKU" value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} />
              <TextInput placeholder="Barcode" value={form.barcode} onChange={(event) => setForm({ ...form, barcode: event.target.value })} />
            </div>
            <Select value={form.category_id} onChange={(event) => setForm({ ...form, category_id: event.target.value })}>
              <option value="">Category</option>
              {(categories.data ?? []).map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </Select>
            <div className="grid grid-cols-2 gap-2">
              <TextInput required type="number" min={0} step="0.01" placeholder="Price" value={form.selling_price} onChange={(event) => setForm({ ...form, selling_price: event.target.value })} />
              <TextInput required type="number" min={0} step="0.01" placeholder="Cost" value={form.cost_price} onChange={(event) => setForm({ ...form, cost_price: event.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <TextInput required type="number" min={0} step="0.01" placeholder="GST" value={form.gst_rate} onChange={(event) => setForm({ ...form, gst_rate: event.target.value })} />
              <TextInput required type="number" min={0} step="0.001" placeholder="Reorder" value={form.reorder_level} onChange={(event) => setForm({ ...form, reorder_level: event.target.value })} />
              <TextInput required placeholder="Unit" value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <TextInput type="number" min={0} step="0.001" placeholder="Opening Qty" value={form.opening_quantity} onChange={(event) => setForm({ ...form, opening_quantity: event.target.value })} />
              <TextInput placeholder="Batch" value={form.opening_batch_number} onChange={(event) => setForm({ ...form, opening_batch_number: event.target.value })} />
            </div>
            <Button disabled={create.isPending} className="w-full">
              <Plus size={16} />
              Save
            </Button>
          </form>
        </Panel>
        <Panel>
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="font-semibold">Catalog</h2>
            <TextInput placeholder="Search" value={search} onChange={(event) => setSearch(event.target.value)} className="max-w-xs" />
          </div>
          {(products.data ?? []).length === 0 ? <EmptyState text="No products" /> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
                  <tr><th className="py-2">Product</th><th>Barcode</th><th>Category</th><th>Price</th><th>Cost</th><th>Stock</th></tr>
                </thead>
                <tbody>
                  {(products.data ?? []).map((product) => (
                    <tr key={product.id} className="border-b border-line last:border-0">
                      <td className="py-3"><div className="font-medium">{product.name}</div><div className="text-xs text-gray-500">{product.sku}</div></td>
                      <td>{product.barcode ?? "-"}</td>
                      <td>{product.category_name ?? "-"}</td>
                      <td>{money(product.selling_price)}</td>
                      <td>{money(product.cost_price)}</td>
                      <td>{product.on_hand}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
