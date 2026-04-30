"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/app-shell";
import { Panel } from "@/components/ui";
import { api } from "@/lib/api";
import { money } from "@/lib/format";

export default function ReportsPage() {
  const revenue = useQuery({
    queryKey: ["reports-revenue-30"],
    queryFn: async () => (await api.get<{ period: string; revenue: string; sales_count: number }[]>("/reports/revenue?days=30")).data
  });
  const top = useQuery({
    queryKey: ["reports-top"],
    queryFn: async () => (await api.get<{ product_name: string; sku: string; quantity_sold: string; revenue: string }[]>("/reports/top-products?limit=20")).data
  });
  return (
    <AppShell title="Reports">
      <div className="grid gap-4 xl:grid-cols-2">
        <Panel>
          <h2 className="mb-4 font-semibold">Revenue</h2>
          <table className="w-full text-sm">
            <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
              <tr><th className="py-2">Date</th><th>Bills</th><th className="text-right">Revenue</th></tr>
            </thead>
            <tbody>
              {(revenue.data ?? []).map((point) => (
                <tr key={point.period} className="border-b border-line last:border-0">
                  <td className="py-2">{point.period}</td>
                  <td>{point.sales_count}</td>
                  <td className="text-right font-medium">{money(point.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
        <Panel>
          <h2 className="mb-4 font-semibold">Top Products</h2>
          <table className="w-full text-sm">
            <thead className="border-b border-line text-left text-xs uppercase tracking-normal text-gray-500">
              <tr><th className="py-2">Product</th><th>Qty</th><th className="text-right">Revenue</th></tr>
            </thead>
            <tbody>
              {(top.data ?? []).map((item) => (
                <tr key={item.sku} className="border-b border-line last:border-0">
                  <td className="py-2"><div className="font-medium">{item.product_name}</div><div className="text-xs text-gray-500">{item.sku}</div></td>
                  <td>{item.quantity_sold}</td>
                  <td className="text-right font-medium">{money(item.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </div>
    </AppShell>
  );
}
