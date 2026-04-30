import { forwardRef } from "react";
import { classNames } from "@/lib/format";

export function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={classNames("rounded border border-line bg-white p-4 shadow-panel", className)}>{children}</section>;
}

export function Button({
  children,
  className = "",
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "danger" }) {
  return (
    <button
      {...props}
      className={classNames(
        "inline-flex items-center justify-center gap-2 rounded px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "bg-mint text-white hover:bg-[#0b855c]",
        variant === "secondary" && "border border-line bg-white text-ink hover:bg-gray-50",
        variant === "danger" && "bg-coral text-white hover:bg-[#bd3434]",
        className
      )}
    >
      {children}
    </button>
  );
}

export const TextInput = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function TextInput(props, ref) {
  return <input ref={ref} {...props} className={classNames("w-full rounded border border-line px-3 py-2 text-sm outline-none focus:border-mint", props.className)} />;
});

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={classNames("w-full rounded border border-line px-3 py-2 text-sm outline-none focus:border-mint", props.className)} />;
}

export function Label({ children }: { children: React.ReactNode }) {
  return <label className="mb-1 block text-xs font-semibold uppercase tracking-normal text-gray-500">{children}</label>;
}

export function EmptyState({ text }: { text: string }) {
  return <div className="rounded border border-dashed border-line bg-gray-50 p-6 text-center text-sm text-gray-500">{text}</div>;
}
