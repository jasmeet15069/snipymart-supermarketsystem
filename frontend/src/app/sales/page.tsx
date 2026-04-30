"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { EmptyState, Panel } from "@/components/ui";
import { api } from "@/lib/api";
import { dateTime, money } from "@/lib/format";
import type { SaleListRow } from "@/lib/types";

export default function SalesPage() {
  const sales = useQuery({ queryKey: ["sales"], queryFn: async () => (await api.get<SaleListRow[]>("/sales")).data });
  return (
    <AppShell title="Sales">
      <Panel>
        {(sales.data ?? []).length === 0 ? <EmptyState text="No sales" /> : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-sm">
              <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
                <tr><th className="py-2">Invoice</th><th>Cashier</th><th>Customer</th><th>Channel / Status</th><th>Payment</th><th>Total</th><th>Created</th></tr>
              </thead>
              <tbody>
                {(sales.data ?? []).map((sale) => (
                  <tr key={sale.id} className="border-b border-line last:border-0">
                    <td className="py-3 font-medium">{sale.invoice_number}</td>
                    <td>{sale.cashier_name}</td>
                    <td>{sale.customer_name ?? "Walk-in"}</td>
                    <td><div>{sale.channel}</div><div className="text-xs text-gray-500">{sale.status}</div></td>
                    <td><div>{sale.payment_status}</div><div className="text-xs text-gray-500">Paid {money(sale.paid_total)}</div></td>
                    <td>{money(sale.grand_total)}</td>
                    <td>{dateTime(sale.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </AppShell>
  );
}
