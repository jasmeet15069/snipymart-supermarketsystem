"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import { dateTime, money } from "@/lib/format";
import type { Product, PurchaseOrder, Supplier } from "@/lib/types";

export default function PurchasesPage() {
  const queryClient = useQueryClient();
  const [poForm, setPoForm] = useState({ supplier_id: "", product_id: "", quantity_ordered: "1", unit_cost: "", gst_rate: "5" });
  const [selectedPoId, setSelectedPoId] = useState("");
  const [grnForm, setGrnForm] = useState({ purchase_order_item_id: "", batch_number: "", expiry_date: "", quantity_received: "1", unit_cost: "" });

  const suppliers = useQuery({ queryKey: ["suppliers"], queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data });
  const products = useQuery({ queryKey: ["products"], queryFn: async () => (await api.get<Product[]>("/products")).data });
  const purchaseOrders = useQuery({ queryKey: ["purchase-orders"], queryFn: async () => (await api.get<PurchaseOrder[]>("/purchase-orders")).data });
  const selectedPo = useQuery({
    queryKey: ["purchase-order", selectedPoId],
    enabled: !!selectedPoId,
    queryFn: async () => (await api.get<PurchaseOrder>(`/purchase-orders/${selectedPoId}`)).data
  });

  const createPo = useMutation({
    mutationFn: async () => (await api.post<PurchaseOrder>("/purchase-orders", {
      supplier_id: Number(poForm.supplier_id),
      items: [{
        product_id: Number(poForm.product_id),
        quantity_ordered: Number(poForm.quantity_ordered),
        unit_cost: Number(poForm.unit_cost),
        gst_rate: Number(poForm.gst_rate)
      }]
    })).data,
    onSuccess: (po) => {
      toast.success(`${po.po_number} saved`);
      setPoForm({ supplier_id: "", product_id: "", quantity_ordered: "1", unit_cost: "", gst_rate: "5" });
      void queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to create purchase order"))
  });

  const receive = useMutation({
    mutationFn: async () => (await api.post(`/purchase-orders/${selectedPoId}/receive`, {
      items: [{
        purchase_order_item_id: Number(grnForm.purchase_order_item_id),
        batch_number: grnForm.batch_number,
        expiry_date: grnForm.expiry_date || null,
        quantity_received: Number(grnForm.quantity_received),
        unit_cost: Number(grnForm.unit_cost)
      }]
    })).data,
    onSuccess: () => {
      toast.success("Goods received");
      setGrnForm({ purchase_order_item_id: "", batch_number: "", expiry_date: "", quantity_received: "1", unit_cost: "" });
      void queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
      void queryClient.invalidateQueries({ queryKey: ["purchase-order", selectedPoId] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to receive goods"))
  });

  function createPoSubmit(event: FormEvent) {
    event.preventDefault();
    createPo.mutate();
  }

  function receiveSubmit(event: FormEvent) {
    event.preventDefault();
    receive.mutate();
  }

  return (
    <AppShell title="Purchases">
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <Panel>
            <form onSubmit={createPoSubmit} className="space-y-3">
              <h2 className="font-semibold">Purchase Order</h2>
              <Select required value={poForm.supplier_id} onChange={(event) => setPoForm({ ...poForm, supplier_id: event.target.value })}>
                <option value="">Supplier</option>
                {(suppliers.data ?? []).map((supplier) => <option key={supplier.id} value={supplier.id}>{supplier.name}</option>)}
              </Select>
              <Select required value={poForm.product_id} onChange={(event) => {
                const product = (products.data ?? []).find((row) => row.id === Number(event.target.value));
                setPoForm({ ...poForm, product_id: event.target.value, unit_cost: product?.cost_price ?? poForm.unit_cost, gst_rate: product?.gst_rate ?? poForm.gst_rate });
              }}>
                <option value="">Product</option>
                {(products.data ?? []).map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}
              </Select>
              <div className="grid grid-cols-3 gap-2">
                <TextInput required type="number" min={0.001} step="0.001" placeholder="Qty" value={poForm.quantity_ordered} onChange={(event) => setPoForm({ ...poForm, quantity_ordered: event.target.value })} />
                <TextInput required type="number" min={0} step="0.01" placeholder="Cost" value={poForm.unit_cost} onChange={(event) => setPoForm({ ...poForm, unit_cost: event.target.value })} />
                <TextInput required type="number" min={0} step="0.01" placeholder="GST" value={poForm.gst_rate} onChange={(event) => setPoForm({ ...poForm, gst_rate: event.target.value })} />
              </div>
              <Button disabled={createPo.isPending} className="w-full">Create PO</Button>
            </form>
          </Panel>
          <Panel>
            <form onSubmit={receiveSubmit} className="space-y-3">
              <h2 className="font-semibold">Goods Receipt</h2>
              <Select required value={selectedPoId} onChange={(event) => setSelectedPoId(event.target.value)}>
                <option value="">Purchase order</option>
                {(purchaseOrders.data ?? []).map((po) => <option key={po.id} value={po.id}>{po.po_number} - {po.status}</option>)}
              </Select>
              <Select required value={grnForm.purchase_order_item_id} onChange={(event) => {
                const item = selectedPo.data?.items?.find((row) => row.id === Number(event.target.value));
                setGrnForm({ ...grnForm, purchase_order_item_id: event.target.value, unit_cost: item?.unit_cost ?? grnForm.unit_cost });
              }}>
                <option value="">PO item</option>
                {(selectedPo.data?.items ?? []).map((item) => <option key={item.id} value={item.id}>Product #{item.product_id} - Rem {Number(item.quantity_ordered) - Number(item.quantity_received)}</option>)}
              </Select>
              <TextInput required placeholder="Batch number" value={grnForm.batch_number} onChange={(event) => setGrnForm({ ...grnForm, batch_number: event.target.value })} />
              <div className="grid grid-cols-3 gap-2">
                <TextInput type="date" value={grnForm.expiry_date} onChange={(event) => setGrnForm({ ...grnForm, expiry_date: event.target.value })} />
                <TextInput required type="number" min={0.001} step="0.001" value={grnForm.quantity_received} onChange={(event) => setGrnForm({ ...grnForm, quantity_received: event.target.value })} />
                <TextInput required type="number" min={0} step="0.01" value={grnForm.unit_cost} onChange={(event) => setGrnForm({ ...grnForm, unit_cost: event.target.value })} />
              </div>
              <Button disabled={receive.isPending || !selectedPoId} className="w-full">Receive</Button>
            </form>
          </Panel>
        </div>
        <Panel>
          {(purchaseOrders.data ?? []).length === 0 ? <EmptyState text="No purchase orders" /> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
                  <tr><th className="py-2">PO</th><th>Supplier</th><th>Status</th><th>Payment</th><th>Total</th><th>Created</th></tr>
                </thead>
                <tbody>{(purchaseOrders.data ?? []).map((po) => (
                  <tr key={po.id} className="border-b border-line last:border-0">
                    <td className="py-3 font-medium">{po.po_number}</td>
                    <td>{po.supplier_name}</td>
                    <td>{po.status}</td>
                    <td>{po.payment_status}</td>
                    <td>{money(po.grand_total)}</td>
                    <td>{dateTime(po.created_at)}</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </AppShell>
  );
}
