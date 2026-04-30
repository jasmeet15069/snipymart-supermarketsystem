"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { EmptyState, Panel } from "@/components/ui";
import { api } from "@/lib/api";
import { dateTime } from "@/lib/format";
import type { InventoryRow } from "@/lib/types";

interface Movement {
  id: number;
  product_name: string | null;
  movement_type: string;
  quantity: string;
  before_quantity: string;
  after_quantity: string;
  reference_type: string | null;
  created_at: string;
}

export default function InventoryPage() {
  const inventory = useQuery({ queryKey: ["inventory"], queryFn: async () => (await api.get<InventoryRow[]>("/inventory")).data });
  const movements = useQuery({ queryKey: ["movements"], queryFn: async () => (await api.get<Movement[]>("/inventory/movements")).data });

  return (
    <AppShell title="Inventory">
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <Panel>
          <h2 className="mb-4 font-semibold">Stock</h2>
          {(inventory.data ?? []).length === 0 ? <EmptyState text="No inventory" /> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[860px] text-sm">
                <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
                  <tr><th className="py-2">Product</th><th>Shelf</th><th>On Hand</th><th>Reorder / Safety</th><th>Batches</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {(inventory.data ?? []).map((row) => (
                    <tr key={row.product_id} className="border-b border-line last:border-0">
                      <td className="py-3"><div className="font-medium">{row.product_name}</div><div className="text-xs text-gray-500">{row.brand ?? row.sku}</div></td>
                      <td>{row.shelf_location ?? "-"}</td>
                      <td>{row.on_hand}</td>
                      <td><div>{row.reorder_level}</div><div className="text-xs text-gray-500">Safety {row.safety_stock}</div></td>
                      <td>{row.batches.map((batch) => `${batch.batch_number}: ${batch.quantity_on_hand}${batch.expiry_date ? ` exp ${batch.expiry_date}` : ""}`).join(", ") || "-"}</td>
                      <td><span className={row.is_low_stock ? "rounded bg-red-50 px-2 py-1 text-xs font-medium text-coral" : "rounded bg-green-50 px-2 py-1 text-xs font-medium text-mint"}>{row.is_low_stock ? "Low" : "OK"}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
        <Panel>
          <h2 className="mb-4 font-semibold">Movements</h2>
          <div className="space-y-3">
            {(movements.data ?? []).map((movement) => (
              <div key={movement.id} className="border-b border-line pb-3 text-sm last:border-0">
                <div className="flex justify-between"><span className="font-medium">{movement.product_name}</span><span>{movement.quantity}</span></div>
                <div className="text-xs text-gray-500">{movement.movement_type} - {movement.before_quantity} to {movement.after_quantity}</div>
                <div className="text-xs text-gray-500">{movement.reference_type ?? "-"} - {dateTime(movement.created_at)}</div>
              </div>
            ))}
            {(movements.data ?? []).length === 0 && <EmptyState text="No movements" />}
          </div>
        </Panel>
      </div>
    </AppShell>
  );
}
