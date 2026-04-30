export function money(value: number | string | null | undefined) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(amount);
}

export function numberValue(value: number | string | null | undefined) {
  return Number(value ?? 0);
}

export function dateTime(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function classNames(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}
