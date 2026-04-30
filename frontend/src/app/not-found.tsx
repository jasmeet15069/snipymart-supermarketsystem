import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f6f8fb] p-4">
      <div className="rounded border border-line bg-white p-6 text-center shadow-panel">
        <h1 className="text-xl font-semibold">Page not found</h1>
        <Link href="/pos" className="mt-4 inline-flex rounded bg-mint px-3 py-2 text-sm font-medium text-white">
          Go to POS
        </Link>
      </div>
    </main>
  );
}
