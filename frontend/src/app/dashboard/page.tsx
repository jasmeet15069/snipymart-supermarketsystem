"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Boxes, IndianRupee, ReceiptText, ShoppingBasket, Users } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { Panel } from "@/components/ui";
import { api } from "@/lib/api";
import { money } from "@/lib/format";
import type { DashboardMetrics } from "@/lib/types";

const metrics = [
  { key: "today_revenue", label: "Today Revenue", icon: IndianRupee },
  { key: "month_revenue", label: "Month Revenue", icon: ReceiptText },
  { key: "today_sales_count", label: "Today Bills", icon: ShoppingBasket },
  { key: "low_stock_count", label: "Low Stock", icon: AlertTriangle },
  { key: "open_purchase_orders", label: "Open POs", icon: Boxes },
  { key: "active_customers", label: "Customers", icon: Users }
] as const;

export default function DashboardPage() {
  const dashboard = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<DashboardMetrics>("/reports/dashboard")).data
  });
  const revenue = useQuery({
    queryKey: ["revenue"],
    queryFn: async () => (await api.get<{ period: string; revenue: string; sales_count: number }[]>("/reports/revenue?days=14")).data
  });
  const top = useQuery({
    queryKey: ["top-products"],
    queryFn: async () => (await api.get<{ product_name: string; quantity_sold: string; revenue: string }[]>("/reports/top-products")).data
  });

  return (
    <AppShell title="Dashboard">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {metrics.map((item) => {
          const Icon = item.icon;
          const raw = dashboard.data?.[item.key] ?? 0;
          const value = String(item.key.includes("revenue") ? money(raw as string) : raw);
          return (
            <Panel key={item.key}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-normal text-gray-500">{item.label}</div>
                  <div className="mt-2 text-2xl font-semibold">{dashboard.isLoading ? "-" : value}</div>
                </div>
                <div className="rounded bg-gray-100 p-3 text-cyan">
                  <Icon size={22} />
                </div>
              </div>
            </Panel>
          );
        })}
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <Panel>
          <h2 className="mb-4 font-semibold">Revenue</h2>
          <div className="space-y-2">
            {(revenue.data ?? []).map((point) => (
              <div key={point.period} className="grid grid-cols-[120px_1fr_100px] items-center gap-3 text-sm">
                <span className="text-gray-500">{point.period}</span>
                <span className="h-2 rounded bg-gray-100">
                  <span className="block h-2 rounded bg-mint" style={{ width: `${Math.min(100, Number(point.revenue) / 500)}%` }} />
                </span>
                <span className="text-right font-medium">{money(point.revenue)}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <h2 className="mb-4 font-semibold">Top Products</h2>
          <div className="space-y-2">
            {(top.data ?? []).map((item) => (
              <div key={item.product_name} className="flex items-center justify-between border-b border-line py-2 text-sm last:border-0">
                <span>{item.product_name}</span>
                <span className="font-medium">{money(item.revenue)}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </AppShell>
  );
}
