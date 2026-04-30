"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import type { Category, Product } from "@/lib/types";

const blank = {
  name: "",
  brand: "",
  sku: "",
  barcode: "",
  hsn_code: "",
  shelf_location: "",
  category_id: "",
  selling_price: "",
  cost_price: "",
  gst_rate: "5",
  min_margin_percent: "12",
  unit: "pcs",
  reorder_level: "5",
  safety_stock: "0",
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
        brand: form.brand || null,
        barcode: form.barcode || null,
        hsn_code: form.hsn_code || null,
        shelf_location: form.shelf_location || null,
        category_id: form.category_id ? Number(form.category_id) : null,
        selling_price: Number(form.selling_price),
        cost_price: Number(form.cost_price),
        gst_rate: Number(form.gst_rate),
        min_margin_percent: Number(form.min_margin_percent),
        reorder_level: Number(form.reorder_level),
        safety_stock: Number(form.safety_stock),
        opening_quantity: Number(form.opening_quantity)
      };
      return (await api.post<Product>("/products", payload)).data;
    },
    onSuccess: () => {
      toast.success("Product saved");
      setForm(blank);
      void queryClient.invalidateQueries({ queryKey: ["products"] });
      void queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to save product"))
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }

  return (
    <AppShell title="Products">
      <div className="grid gap-4 xl:grid-cols-[380px_1fr]">
        <Panel>
          <form onSubmit={submit} className="space-y-3">
            <h2 className="font-semibold">New Product</h2>
            <TextInput required placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            <div className="grid grid-cols-2 gap-2">
              <TextInput placeholder="Brand" value={form.brand} onChange={(event) => setForm({ ...form, brand: event.target.value })} />
              <TextInput required placeholder="SKU" value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <TextInput placeholder="Barcode" value={form.barcode} onChange={(event) => setForm({ ...form, barcode: event.target.value })} />
              <TextInput placeholder="HSN" value={form.hsn_code} onChange={(event) => setForm({ ...form, hsn_code: event.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <Select value={form.category_id} onChange={(event) => setForm({ ...form, category_id: event.target.value })}>
                <option value="">Category</option>
                {(categories.data ?? []).map((category) => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </Select>
              <TextInput placeholder="Shelf" value={form.shelf_location} onChange={(event) => setForm({ ...form, shelf_location: event.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <TextInput required type="number" min={0} step="0.01" placeholder="Price" value={form.selling_price} onChange={(event) => setForm({ ...form, selling_price: event.target.value })} />
              <TextInput required type="number" min={0} step="0.01" placeholder="Cost" value={form.cost_price} onChange={(event) => setForm({ ...form, cost_price: event.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <TextInput required type="number" min={0} step="0.01" placeholder="GST" value={form.gst_rate} onChange={(event) => setForm({ ...form, gst_rate: event.target.value })} />
              <TextInput required type="number" min={0} step="0.01" placeholder="Margin" value={form.min_margin_percent} onChange={(event) => setForm({ ...form, min_margin_percent: event.target.value })} />
              <TextInput required placeholder="Unit" value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <TextInput required type="number" min={0} step="0.001" placeholder="Reorder" value={form.reorder_level} onChange={(event) => setForm({ ...form, reorder_level: event.target.value })} />
              <TextInput required type="number" min={0} step="0.001" placeholder="Safety" value={form.safety_stock} onChange={(event) => setForm({ ...form, safety_stock: event.target.value })} />
              <TextInput type="number" min={0} step="0.001" placeholder="Opening" value={form.opening_quantity} onChange={(event) => setForm({ ...form, opening_quantity: event.target.value })} />
            </div>
            <TextInput placeholder="Opening batch" value={form.opening_batch_number} onChange={(event) => setForm({ ...form, opening_batch_number: event.target.value })} />
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
              <table className="w-full min-w-[980px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
                  <tr><th className="py-2">Product</th><th>Brand</th><th>Barcode / HSN</th><th>Category / Shelf</th><th>Price / Cost</th><th>Stock / Safety</th></tr>
                </thead>
                <tbody>
                  {(products.data ?? []).map((product) => (
                    <tr key={product.id} className="border-b border-line last:border-0">
                      <td className="py-3"><div className="font-medium">{product.name}</div><div className="text-xs text-gray-500">{product.sku}</div></td>
                      <td>{product.brand ?? "-"}</td>
                      <td><div>{product.barcode ?? "-"}</div><div className="text-xs text-gray-500">HSN {product.hsn_code ?? "-"}</div></td>
                      <td><div>{product.category_name ?? "-"}</div><div className="text-xs text-gray-500">{product.shelf_location ?? "No shelf"}</div></td>
                      <td><div>{money(product.selling_price)}</div><div className="text-xs text-gray-500">Cost {money(product.cost_price)}</div></td>
                      <td><div>{product.on_hand}</div><div className="text-xs text-gray-500">Safety {product.safety_stock}</div></td>
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
