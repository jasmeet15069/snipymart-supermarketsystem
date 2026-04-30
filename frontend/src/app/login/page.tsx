"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { LockKeyhole, Store, UserRound } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/components/providers";
import { apiErrorMessage } from "@/lib/api";
import { Button, TextInput } from "@/components/ui";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@snipymart.in");
  const [password, setPassword] = useState("Admin@12345");
  const [busy, setBusy] = useState(false);

  async function signIn(nextEmail = email, nextPassword = password) {
    setBusy(true);
    try {
      await login(nextEmail.trim(), nextPassword);
      router.replace("/pos");
    } catch (error) {
      toast.error(apiErrorMessage(error, "Unable to sign in"));
    } finally {
      setBusy(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await signIn();
  }

  async function demoLogin(role: "admin" | "cashier") {
    const credentials =
      role === "admin"
        ? { email: "admin@snipymart.in", password: "Admin@12345" }
        : { email: "cashier@snipymart.in", password: "Cashier@12345" };
    setEmail(credentials.email);
    setPassword(credentials.password);
    await signIn(credentials.email, credentials.password);
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f6f8fb] p-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded border border-line bg-white p-6 shadow-panel">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded bg-mint text-white">
            <Store size={24} />
          </div>
          <div>
            <h1 className="text-xl font-semibold">SnipyMart ERP</h1>
            <p className="text-sm text-gray-500">Supermarket POS</p>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <TextInput value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <TextInput value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </div>
          <Button disabled={busy} className="w-full">
            <LockKeyhole size={16} />
            {busy ? "Signing in" : "Sign in"}
          </Button>
          <div className="grid grid-cols-2 gap-2">
            <Button type="button" variant="secondary" disabled={busy} onClick={() => void demoLogin("admin")}>
              <UserRound size={15} />
              Admin
            </Button>
            <Button type="button" variant="secondary" disabled={busy} onClick={() => void demoLogin("cashier")}>
              <UserRound size={15} />
              Cashier
            </Button>
          </div>
        </div>
      </form>
    </main>
  );
}
