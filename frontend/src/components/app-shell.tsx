"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  BarChart3,
  Boxes,
  Contact,
  LayoutDashboard,
  LogOut,
  Package,
  ReceiptText,
  ShoppingCart,
  Truck,
  Users
} from "lucide-react";
import { useAuth } from "@/components/providers";
import { classNames } from "@/lib/format";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, admin: true },
  { href: "/pos", label: "POS", icon: ShoppingCart },
  { href: "/products", label: "Products", icon: Package, admin: true },
  { href: "/inventory", label: "Inventory", icon: Boxes, admin: true },
  { href: "/sales", label: "Sales", icon: ReceiptText },
  { href: "/reports", label: "Reports", icon: BarChart3, admin: true },
  { href: "/suppliers", label: "Suppliers", icon: Truck, admin: true },
  { href: "/purchases", label: "Purchases", icon: ReceiptText, admin: true },
  { href: "/customers", label: "Customers", icon: Contact },
  { href: "/settings/users", label: "Users", icon: Users, admin: true }
];

export function AppShell({ children, title }: { children: React.ReactNode; title: string }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-gray-600">Loading</div>;
  }

  return (
    <div className="min-h-screen bg-[#f6f8fb]">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-white px-3 py-4 lg:block">
        <div className="mb-5 flex items-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-mint text-lg font-bold text-white">S</div>
          <div>
            <div className="font-semibold">SnipyMart</div>
            <div className="text-xs text-gray-500">{user.role}</div>
          </div>
        </div>
        <nav className="space-y-1">
          {nav
            .filter((item) => !item.admin || user.role === "ADMIN")
            .map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={classNames(
                    "flex items-center gap-3 rounded px-3 py-2 text-sm font-medium",
                    active ? "bg-mint text-white" : "text-gray-700 hover:bg-gray-100"
                  )}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-white/95 px-4 backdrop-blur lg:px-8">
          <div>
            <h1 className="text-lg font-semibold">{title}</h1>
            <p className="text-xs text-gray-500">{user.full_name}</p>
          </div>
          <button
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="inline-flex items-center gap-2 rounded border border-line bg-white px-3 py-2 text-sm hover:bg-gray-50"
          >
            <LogOut size={16} />
            Sign out
          </button>
        </header>
        <div className="p-4 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
