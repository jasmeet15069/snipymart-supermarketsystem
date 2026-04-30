"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  Banknote,
  Camera,
  CreditCard,
  Keyboard,
  Minus,
  Package,
  PauseCircle,
  Plus,
  Printer,
  QrCode,
  ReceiptText,
  RotateCcw,
  ScanBarcode,
  Search,
  ShieldCheck,
  ShoppingCart,
  Trash2,
  UserRound,
  X
} from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { Button, EmptyState, Panel, Select, TextInput } from "@/components/ui";
import { api, apiErrorMessage } from "@/lib/api";
import { classNames, dateTime, money, numberValue } from "@/lib/format";
import type { Customer, PaymentMode, Product, Sale, Shift } from "@/lib/types";

interface CartLine {
  product: Product;
  quantity: number;
  discount_amount: number;
}

interface HeldBill {
  id: string;
  createdAt: string;
  customerId: string;
  lines: CartLine[];
}

interface BarcodeResult {
  rawValue: string;
}

interface BarcodeDetectorInstance {
  detect(source: CanvasImageSource): Promise<BarcodeResult[]>;
}

type BarcodeDetectorConstructor = new (options?: { formats?: string[] }) => BarcodeDetectorInstance;

const paymentModes: Array<{ mode: PaymentMode; label: string; icon: typeof Banknote }> = [
  { mode: "CASH", label: "Cash", icon: Banknote },
  { mode: "UPI", label: "UPI", icon: QrCode },
  { mode: "CARD", label: "Card", icon: CreditCard }
];

function taxSplit(total: number, gstRate: number) {
  if (gstRate <= 0) return { taxable: total, tax: 0 };
  const taxable = (total * 100) / (100 + gstRate);
  return { taxable, tax: total - taxable };
}

function loadHeldBills(): HeldBill[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(window.localStorage.getItem("snipymart_held_bills") ?? "[]");
  } catch {
    return [];
  }
}

export default function POSPage() {
  const queryClient = useQueryClient();
  const searchRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const scannerStreamRef = useRef<MediaStream | null>(null);
  const scannerLoopRef = useRef<number | null>(null);
  const lastScanRef = useRef<{ code: string; at: number } | null>(null);
  const handleScannedBarcodeRef = useRef<(code: string) => Promise<void>>(async () => undefined);
  const [query, setQuery] = useState("");
  const [cart, setCart] = useState<CartLine[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [paymentMode, setPaymentMode] = useState<PaymentMode>("CASH");
  const [amountTendered, setAmountTendered] = useState("");
  const [openingCash, setOpeningCash] = useState("0");
  const [closingCash, setClosingCash] = useState("");
  const [lastSale, setLastSale] = useState<Sale | null>(null);
  const [heldBills, setHeldBills] = useState<HeldBill[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [scannerOpen, setScannerOpen] = useState(false);
  const [scannerStatus, setScannerStatus] = useState("Ready to scan");
  const [scannerAutoAdd, setScannerAutoAdd] = useState(true);
  const [scannerProduct, setScannerProduct] = useState<Product | null>(null);
  const [scannedCode, setScannedCode] = useState("");
  const [manualBarcode, setManualBarcode] = useState("");

  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: async () => (await api.get<Customer[]>("/customers")).data
  });
  const products = useQuery({
    queryKey: ["products", "pos"],
    queryFn: async () => (await api.get<Product[]>("/products")).data
  });
  const lookup = useQuery({
    queryKey: ["product-lookup", query.trim()],
    enabled: query.trim().length > 0,
    queryFn: async () => (await api.get<Product[]>("/products/lookup", { params: { query } })).data
  });
  const shift = useQuery({
    queryKey: ["current-shift"],
    queryFn: async () => (await api.get<Shift | null>("/shifts/current")).data
  });

  useEffect(() => {
    searchRef.current?.focus();
    queueMicrotask(() => {
      const savedCart = window.localStorage.getItem("snipymart_cart");
      if (savedCart) setCart(JSON.parse(savedCart));
      setHeldBills(loadHeldBills());
    });
  }, []);

  useEffect(() => {
    window.localStorage.setItem("snipymart_cart", JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    window.localStorage.setItem("snipymart_held_bills", JSON.stringify(heldBills));
  }, [heldBills]);

  useEffect(() => {
    if (!scannerOpen) {
      stopScanner();
      return;
    }

    let cancelled = false;
    async function startScanner() {
      setScannerStatus("Starting camera...");
      setScannerProduct(null);
      setScannedCode("");
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false
        });
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }
        scannerStreamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        const Detector = (window as unknown as { BarcodeDetector?: BarcodeDetectorConstructor }).BarcodeDetector;
        if (!Detector) {
          setScannerStatus("Camera is open. Native barcode detection is unavailable here; use manual barcode entry or a USB scanner.");
          return;
        }
        const detector = new Detector({ formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39", "qr_code"] });
        setScannerStatus("Point the camera at a barcode");
        const scan = async () => {
          if (!videoRef.current || cancelled) return;
          try {
            if (videoRef.current.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
              const codes = await detector.detect(videoRef.current);
              const code = codes[0]?.rawValue?.trim();
              if (code) {
                const last = lastScanRef.current;
                const now = Date.now();
                if (!last || last.code !== code || now - last.at > 2200) {
                  lastScanRef.current = { code, at: now };
                  await handleScannedBarcodeRef.current(code);
                }
              }
            }
          } catch {
            setScannerStatus("Scanner is active. Keep the barcode inside the frame.");
          }
          scannerLoopRef.current = window.setTimeout(scan, 450);
        };
        void scan();
      } catch {
        setScannerStatus("Camera access failed. Use manual barcode entry or allow camera permission.");
      }
    }

    void startScanner();
    return () => {
      cancelled = true;
      stopScanner();
    };
  }, [scannerOpen]);

  const categories = useMemo(() => {
    const names = new Set((products.data ?? []).map((product) => product.category_name ?? "Uncategorised"));
    return ["All", ...Array.from(names).sort()];
  }, [products.data]);

  const productTiles = useMemo(() => {
    const source = query.trim() ? lookup.data ?? [] : products.data ?? [];
    return source
      .filter((product) => selectedCategory === "All" || (product.category_name ?? "Uncategorised") === selectedCategory)
      .sort((a, b) => numberValue(b.on_hand) - numberValue(a.on_hand))
      .slice(0, 24);
  }, [lookup.data, products.data, query, selectedCategory]);

  const totals = useMemo(() => {
    return cart.reduce(
      (acc, line) => {
        const gross = numberValue(line.product.selling_price) * line.quantity;
        const discount = Math.min(line.discount_amount, gross);
        const lineTotal = gross - discount;
        const split = taxSplit(lineTotal, numberValue(line.product.gst_rate));
        acc.subtotal += gross;
        acc.discount += discount;
        acc.taxable += split.taxable;
        acc.tax += split.tax;
        acc.total += lineTotal;
        acc.items += line.quantity;
        return acc;
      },
      { subtotal: 0, discount: 0, taxable: 0, tax: 0, total: 0, items: 0 }
    );
  }, [cart]);

  const tendered = numberValue(amountTendered);
  const balanceDue = Math.max(0, totals.total - tendered);
  const changeDue = Math.max(0, tendered - totals.total);
  const cashNeedsShift = paymentMode === "CASH" && !shift.data;

  useEffect(() => {
    queueMicrotask(() => setAmountTendered(totals.total ? totals.total.toFixed(2) : ""));
  }, [totals.total]);

  function setQuantity(productId: number, nextQuantity: number) {
    setCart((current) =>
      current.map((line) => {
        if (line.product.id !== productId) return line;
        const maxStock = Math.max(1, numberValue(line.product.on_hand));
        return { ...line, quantity: Math.min(maxStock, Math.max(1, nextQuantity)) };
      })
    );
  }

  function setDiscount(productId: number, discount: number) {
    setCart((current) =>
      current.map((line) => {
        if (line.product.id !== productId) return line;
        const maxDiscount = numberValue(line.product.selling_price) * line.quantity;
        return { ...line, discount_amount: Math.min(maxDiscount, Math.max(0, discount)) };
      })
    );
  }

  function stopScanner() {
    if (scannerLoopRef.current) {
      window.clearTimeout(scannerLoopRef.current);
      scannerLoopRef.current = null;
    }
    if (scannerStreamRef.current) {
      scannerStreamRef.current.getTracks().forEach((track) => track.stop());
      scannerStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }

  async function findProductByBarcode(code: string) {
    const local = (products.data ?? []).find((product) => product.barcode === code || product.sku === code);
    if (local) return local;
    const response = await api.get<Product[]>("/products/lookup", { params: { query: code } });
    return response.data.find((product) => product.barcode === code || product.sku === code) ?? response.data[0] ?? null;
  }

  async function handleScannedBarcode(code: string) {
    setScannedCode(code);
    setScannerStatus(`Scanned ${code}. Looking up product...`);
    try {
      const product = await findProductByBarcode(code);
      if (!product) {
        setScannerProduct(null);
        setScannerStatus(`No product found for ${code}`);
        toast.error(`No product found for ${code}`);
        return;
      }
      setScannerProduct(product);
      setScannerStatus(`${product.name} found`);
      if (scannerAutoAdd) {
        addProduct(product);
        toast.success(`${product.name} added from barcode`);
      }
    } catch {
      setScannerProduct(null);
      setScannerStatus("Barcode lookup failed. Check the API connection and try again.");
    }
  }

  async function submitManualBarcode(event: FormEvent) {
    event.preventDefault();
    const code = manualBarcode.trim();
    if (!code) return;
    await handleScannedBarcode(code);
    setManualBarcode("");
  }

  useEffect(() => {
    handleScannedBarcodeRef.current = handleScannedBarcode;
  });

  function addProduct(product: Product) {
    const stock = numberValue(product.on_hand);
    if (stock <= 0) {
      toast.error("No stock available");
      return;
    }
    setCart((current) => {
      const existing = current.find((line) => line.product.id === product.id);
      if (existing) {
        if (existing.quantity >= stock) {
          toast.warning("Cart quantity already matches available stock");
          return current;
        }
        return current.map((line) => (line.product.id === product.id ? { ...line, quantity: line.quantity + 1 } : line));
      }
      return [...current, { product, quantity: 1, discount_amount: 0 }];
    });
    setQuery("");
    searchRef.current?.focus();
  }

  function submitLookup(event: FormEvent) {
    event.preventDefault();
    const candidates = lookup.data ?? [];
    if (candidates.length > 0) addProduct(candidates[0]);
  }

  function holdBill() {
    if (!cart.length) return;
    const held: HeldBill = {
      id: `H${Date.now().toString().slice(-6)}`,
      createdAt: new Date().toISOString(),
      customerId,
      lines: cart
    };
    setHeldBills((current) => [held, ...current].slice(0, 8));
    setCart([]);
    setCustomerId("");
    toast.success(`Bill ${held.id} held`);
  }

  function recallBill(held: HeldBill) {
    if (cart.length) {
      toast.error("Clear or hold the current cart before recall");
      return;
    }
    setCart(held.lines);
    setCustomerId(held.customerId);
    setHeldBills((current) => current.filter((bill) => bill.id !== held.id));
    toast.success(`Bill ${held.id} recalled`);
  }

  const checkout = useMutation({
    mutationFn: async () => {
      const response = await api.post<Sale>("/sales", {
        customer_id: customerId ? Number(customerId) : null,
        items: cart.map((line) => ({
          product_id: line.product.id,
          quantity: line.quantity,
          discount_amount: line.discount_amount
        })),
        payments: [{ mode: paymentMode, amount: Number(amountTendered || totals.total) }]
      });
      return response.data;
    },
    onSuccess: (sale) => {
      setLastSale(sale);
      setCart([]);
      setCustomerId("");
      setQuery("");
      toast.success(`Invoice ${sale.invoice_number} saved`);
      void queryClient.invalidateQueries({ queryKey: ["products"] });
      void queryClient.invalidateQueries({ queryKey: ["inventory"] });
      void queryClient.invalidateQueries({ queryKey: ["current-shift"] });
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Sale failed"))
  });

  const openShift = useMutation({
    mutationFn: async () => (await api.post<Shift>("/shifts/open", { opening_cash: Number(openingCash || 0) })).data,
    onSuccess: () => {
      toast.success("Shift opened");
      setOpeningCash("0");
      void shift.refetch();
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to open shift"))
  });

  const closeShift = useMutation({
    mutationFn: async () => {
      if (!shift.data) return null;
      return (await api.post<Shift>(`/shifts/${shift.data.id}/close`, { closing_cash: Number(closingCash || 0) })).data;
    },
    onSuccess: () => {
      toast.success("Shift closed");
      setClosingCash("");
      void shift.refetch();
    },
    onError: (error) => toast.error(apiErrorMessage(error, "Unable to close shift"))
  });

  const checkoutBlocked = !cart.length || checkout.isPending || balanceDue > 0 || cashNeedsShift;

  return (
    <AppShell title="POS">
      <div className="space-y-4">
        <div className="grid gap-3 md:grid-cols-4 no-print">
          <StatusTile label="Shift" value={shift.data ? `Open #${shift.data.id}` : "Closed"} tone={shift.data ? "green" : "red"} icon={ShieldCheck} />
          <StatusTile label="Cart" value={`${cart.length} lines / ${totals.items} qty`} tone="blue" icon={ShoppingCart} />
          <StatusTile label="Total" value={money(totals.total)} tone="dark" icon={ReceiptText} />
          <StatusTile label="Change" value={money(changeDue)} tone={changeDue > 0 ? "green" : "amber"} icon={Banknote} />
        </div>

        <div className="grid gap-4 2xl:grid-cols-[minmax(0,1fr)_420px]">
          <div className="space-y-4">
            <Panel className="no-print">
              <form onSubmit={submitLookup} className="flex flex-col gap-3 lg:flex-row">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute left-3 top-3.5 text-gray-400" size={18} />
                  <TextInput
                    ref={searchRef}
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Scan barcode or search products"
                    className="h-12 pl-10 text-base"
                  />
                </div>
                <div className="grid grid-cols-3 gap-2 lg:w-[390px]">
                  <Button type="submit" className="h-12">
                    <Plus size={18} />
                    Add
                  </Button>
                  <Button type="button" variant="secondary" className="h-12" onClick={() => setScannerOpen((value) => !value)}>
                    <ScanBarcode size={18} />
                    Scanner
                  </Button>
                  <Button type="button" variant="secondary" className="h-12" onClick={() => setQuery("")}>
                    <X size={18} />
                    Clear
                  </Button>
                </div>
              </form>

              {scannerOpen && (
                <div className="mt-4 grid gap-4 rounded border border-line bg-gray-50 p-3 lg:grid-cols-[minmax(0,1fr)_340px]">
                  <div className="relative overflow-hidden rounded bg-black">
                    <video ref={videoRef} className="aspect-video w-full object-cover" muted playsInline />
                    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                      <div className="h-28 w-72 max-w-[80%] rounded border-2 border-mint shadow-[0_0_0_999px_rgba(0,0,0,0.35)]" />
                    </div>
                    <div className="absolute left-3 top-3 rounded bg-black/70 px-3 py-1 text-xs font-medium text-white">
                      {scannerStatus}
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2 font-semibold"><Camera size={18} /> Barcode scanner</div>
                        <p className="text-xs text-gray-500">Camera scanning works on localhost or HTTPS. USB barcode scanners can type into the search field.</p>
                      </div>
                      <Button type="button" variant="secondary" onClick={() => setScannerOpen(false)}>
                        <X size={16} />
                        Close
                      </Button>
                    </div>
                    <label className="flex items-center gap-2 text-sm">
                      <input type="checkbox" checked={scannerAutoAdd} onChange={(event) => setScannerAutoAdd(event.target.checked)} />
                      Auto-add matched product to cart
                    </label>
                    <form onSubmit={submitManualBarcode} className="grid grid-cols-[1fr_auto] gap-2">
                      <TextInput value={manualBarcode} onChange={(event) => setManualBarcode(event.target.value)} placeholder="Enter barcode manually" />
                      <Button type="submit" variant="secondary">
                        <Keyboard size={16} />
                        Lookup
                      </Button>
                    </form>
                    {scannedCode && (
                      <div className="rounded border border-line bg-white p-3 text-sm">
                        <div className="text-xs font-semibold uppercase tracking-normal text-gray-500">Last barcode</div>
                        <div className="font-mono text-base">{scannedCode}</div>
                      </div>
                    )}
                    {scannerProduct && (
                      <div className="rounded border border-line bg-white p-3 text-sm">
                        <div className="mb-2 flex items-start justify-between gap-3">
                          <div>
                            <div className="font-semibold">{scannerProduct.name}</div>
                            <div className="text-xs text-gray-500">{scannerProduct.sku} - {scannerProduct.brand ?? scannerProduct.category_name ?? "Uncategorised"}</div>
                          </div>
                          <span className="font-semibold">{money(scannerProduct.selling_price)}</span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div className="rounded bg-gray-50 p-2"><span className="block text-gray-500">Stock</span>{scannerProduct.on_hand}</div>
                          <div className="rounded bg-gray-50 p-2"><span className="block text-gray-500">GST</span>{scannerProduct.gst_rate}%</div>
                          <div className="rounded bg-gray-50 p-2"><span className="block text-gray-500">Shelf</span>{scannerProduct.shelf_location ?? "-"}</div>
                        </div>
                        <Button type="button" className="mt-3 w-full" onClick={() => addProduct(scannerProduct)}>
                          <Plus size={16} />
                          Add product
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
                {categories.map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={classNames(
                      "whitespace-nowrap rounded border px-3 py-2 text-sm font-medium",
                      selectedCategory === category ? "border-mint bg-mint text-white" : "border-line bg-white hover:bg-gray-50"
                    )}
                  >
                    {category}
                  </button>
                ))}
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {productTiles.map((product) => (
                  <button
                    key={product.id}
                    onClick={() => addProduct(product)}
                    className="rounded border border-line bg-white p-3 text-left transition hover:border-mint hover:shadow-panel disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={numberValue(product.on_hand) <= 0}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="line-clamp-2 font-semibold">{product.name}</div>
                        <div className="mt-1 text-xs text-gray-500">{product.brand ? `${product.brand} - ${product.barcode ?? product.sku}` : product.barcode ?? product.sku}</div>
                      </div>
                      <Package size={18} className="shrink-0 text-cyan" />
                    </div>
                    <div className="mt-3 flex items-center justify-between">
                      <span className="font-semibold">{money(product.selling_price)}</span>
                      <span className={classNames("rounded px-2 py-1 text-xs font-medium", numberValue(product.on_hand) <= numberValue(product.reorder_level) ? "bg-amber-50 text-amber" : "bg-green-50 text-mint")}>
                        Stock {product.on_hand}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </Panel>

            <Panel className="p-0">
              <div className="flex items-center justify-between border-b border-line p-4">
                <div>
                  <h2 className="font-semibold">Current Bill</h2>
                  <p className="text-xs text-gray-500">{cart.length ? `${cart.length} products ready for checkout` : "Add products to start billing"}</p>
                </div>
                <div className="flex gap-2 no-print">
                  <Button type="button" variant="secondary" disabled={!cart.length} onClick={holdBill}>
                    <PauseCircle size={16} />
                    Hold
                  </Button>
                  <Button type="button" variant="danger" disabled={!cart.length} onClick={() => setCart([])}>
                    <Trash2 size={16} />
                    Clear
                  </Button>
                </div>
              </div>

              {cart.length === 0 ? (
                <div className="p-4">
                  <EmptyState text="Cart is empty" />
                </div>
              ) : (
                <div className="divide-y divide-line">
                  {cart.map((line) => {
                    const gross = numberValue(line.product.selling_price) * line.quantity;
                    const lineTotal = gross - line.discount_amount;
                    const isLowAfterSale = numberValue(line.product.on_hand) - line.quantity <= numberValue(line.product.reorder_level);
                    return (
                      <div key={line.product.id} className="grid gap-3 p-4 lg:grid-cols-[minmax(0,1fr)_150px_140px_120px_42px] lg:items-center">
                        <div>
                          <div className="font-semibold">{line.product.name}</div>
                          <div className="mt-1 flex flex-wrap gap-2 text-xs text-gray-500">
                            <span>{line.product.sku}</span>
                            <span>GST {line.product.gst_rate}%</span>
                            <span>{money(line.product.selling_price)}</span>
                            {isLowAfterSale && <span className="text-amber">low after sale</span>}
                          </div>
                        </div>
                        <div className="flex h-10 w-[150px] items-center rounded border border-line">
                          <button title="Decrease quantity" className="p-3" onClick={() => setQuantity(line.product.id, line.quantity - 1)}>
                            <Minus size={14} />
                          </button>
                          <input
                            value={line.quantity}
                            onChange={(event) => setQuantity(line.product.id, Number(event.target.value || 1))}
                            className="h-full w-full border-x border-line text-center outline-none"
                          />
                          <button title="Increase quantity" className="p-3" onClick={() => setQuantity(line.product.id, line.quantity + 1)}>
                            <Plus size={14} />
                          </button>
                        </div>
                        <TextInput
                          aria-label={`Discount for ${line.product.name}`}
                          type="number"
                          min={0}
                          value={line.discount_amount}
                          onChange={(event) => setDiscount(line.product.id, Number(event.target.value || 0))}
                        />
                        <div className="text-right font-semibold">{money(lineTotal)}</div>
                        <button
                          title="Remove item"
                          onClick={() => setCart((current) => current.filter((row) => row.product.id !== line.product.id))}
                          className="rounded p-2 text-coral hover:bg-red-50"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </Panel>
          </div>

          <aside className="space-y-4">
            <Panel className="no-print">
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold">Shift Control</h2>
                  <p className="text-xs text-gray-500">{shift.data ? `Opened ${dateTime(shift.data.opened_at)}` : "Cash drawer is closed"}</p>
                </div>
                {!shift.data && <AlertTriangle size={20} className="text-amber" />}
              </div>
              {shift.data ? (
                <div className="grid grid-cols-[1fr_auto] gap-2">
                  <TextInput type="number" min={0} value={closingCash} onChange={(event) => setClosingCash(event.target.value)} placeholder="Closing cash" />
                  <Button variant="secondary" disabled={closeShift.isPending || !closingCash} onClick={() => closeShift.mutate()}>
                    Close
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-[1fr_auto] gap-2">
                  <TextInput type="number" min={0} value={openingCash} onChange={(event) => setOpeningCash(event.target.value)} placeholder="Opening cash" />
                  <Button variant="secondary" disabled={openShift.isPending} onClick={() => openShift.mutate()}>
                    Open
                  </Button>
                </div>
              )}
            </Panel>

            <Panel className="no-print">
              <div className="mb-3 flex items-center gap-2">
                <UserRound size={18} className="text-cyan" />
                <h2 className="font-semibold">Customer</h2>
              </div>
              <Select value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
                <option value="">Walk-in customer</option>
                {(customers.data ?? []).map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name} {customer.phone ? `(${customer.phone})` : ""}
                  </option>
                ))}
              </Select>
            </Panel>

            <Panel className="no-print">
              <h2 className="mb-3 font-semibold">Payment</h2>
              <div className="grid grid-cols-3 gap-2">
                {paymentModes.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.mode}
                      onClick={() => setPaymentMode(item.mode)}
                      className={classNames(
                        "rounded border p-3 text-center text-sm font-medium",
                        paymentMode === item.mode ? "border-mint bg-green-50 text-mint" : "border-line bg-white hover:bg-gray-50"
                      )}
                    >
                      <Icon size={18} className="mx-auto mb-1" />
                      {item.label}
                    </button>
                  );
                })}
              </div>
              <div className="mt-3">
                <TextInput type="number" min={0} value={amountTendered} onChange={(event) => setAmountTendered(event.target.value)} placeholder="Amount tendered" />
              </div>
              <div className="mt-3 grid grid-cols-4 gap-2">
                {[totals.total, totals.total + 50, totals.total + 100, totals.total + 500].map((value, index) => (
                  <button
                    key={`${value}-${index}`}
                    disabled={!totals.total}
                    onClick={() => setAmountTendered(value.toFixed(2))}
                    className="rounded border border-line bg-white px-2 py-2 text-xs font-medium hover:bg-gray-50 disabled:opacity-50"
                  >
                    {index === 0 ? "Exact" : money(value)}
                  </button>
                ))}
              </div>
              {cashNeedsShift && (
                <div className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber">
                  Open a shift before accepting cash.
                </div>
              )}
            </Panel>

            <Panel>
              <div className="space-y-2 text-sm">
                <SummaryRow label="Subtotal" value={money(totals.subtotal)} />
                <SummaryRow label="Discount" value={money(totals.discount)} />
                <SummaryRow label="Taxable" value={money(totals.taxable)} />
                <SummaryRow label="GST" value={money(totals.tax)} />
                <div className="border-t border-line pt-3">
                  <SummaryRow label="Grand Total" value={money(totals.total)} strong />
                  <SummaryRow label="Balance" value={money(balanceDue)} />
                  <SummaryRow label="Change" value={money(changeDue)} />
                </div>
                <Button disabled={checkoutBlocked} onClick={() => checkout.mutate()} className="mt-4 h-12 w-full text-base">
                  <ReceiptText size={18} />
                  Complete Sale
                </Button>
              </div>
            </Panel>

            {heldBills.length > 0 && (
              <Panel className="no-print">
                <h2 className="mb-3 font-semibold">Held Bills</h2>
                <div className="space-y-2">
                  {heldBills.map((bill) => (
                    <div key={bill.id} className="flex items-center justify-between rounded border border-line p-2 text-sm">
                      <div>
                        <div className="font-medium">{bill.id}</div>
                        <div className="text-xs text-gray-500">{bill.lines.length} lines</div>
                      </div>
                      <button onClick={() => recallBill(bill)} className="rounded p-2 text-cyan hover:bg-blue-50" title="Recall bill">
                        <RotateCcw size={17} />
                      </button>
                    </div>
                  ))}
                </div>
              </Panel>
            )}

            {lastSale && (
              <Panel>
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold">{lastSale.invoice_number}</div>
                    <div className="text-xs text-gray-500">{dateTime(lastSale.created_at)}</div>
                  </div>
                  <Button variant="secondary" onClick={() => window.print()}>
                    <Printer size={16} />
                    Print
                  </Button>
                </div>
                <Receipt sale={lastSale} />
              </Panel>
            )}
          </aside>
        </div>
      </div>
      {lastSale && (
        <div className="receipt-print hidden">
          <Receipt sale={lastSale} />
        </div>
      )}
    </AppShell>
  );
}

function StatusTile({
  label,
  value,
  icon: Icon,
  tone
}: {
  label: string;
  value: string;
  icon: typeof Banknote;
  tone: "green" | "red" | "blue" | "amber" | "dark";
}) {
  const tones = {
    green: "bg-green-50 text-mint",
    red: "bg-red-50 text-coral",
    blue: "bg-blue-50 text-cyan",
    amber: "bg-amber-50 text-amber",
    dark: "bg-gray-100 text-ink"
  };
  return (
    <Panel className="p-3">
      <div className="flex items-center gap-3">
        <div className={classNames("rounded p-2", tones[tone])}>
          <Icon size={18} />
        </div>
        <div className="min-w-0">
          <div className="text-xs font-semibold uppercase tracking-normal text-gray-500">{label}</div>
          <div className="truncate font-semibold">{value}</div>
        </div>
      </div>
    </Panel>
  );
}

function SummaryRow({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className={classNames("flex justify-between", strong && "text-lg font-semibold")}>
      <span>{label}</span>
      <span>{value}</span>
    </div>
  );
}

function Receipt({ sale }: { sale: Sale }) {
  return (
    <div className="text-xs">
      <div className="mb-2 text-center">
        <div className="font-bold">SNIPYMART</div>
        <div>GSTIN: 29ABCDE1234F1Z5</div>
        <div>{sale.invoice_number}</div>
      </div>
      <table className="w-full">
        <tbody>
          {sale.items.map((item) => (
            <tr key={item.id} className="border-b border-dashed border-gray-300">
              <td className="py-1">
                <div>{item.product_name}</div>
                <div>
                  {item.quantity} x {money(item.unit_price)}
                </div>
              </td>
              <td className="py-1 text-right">{money(item.line_total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2 space-y-1">
        <div className="flex justify-between">
          <span>Taxable</span>
          <span>{money(sale.taxable_total)}</span>
        </div>
        <div className="flex justify-between">
          <span>GST</span>
          <span>{money(sale.tax_total)}</span>
        </div>
        <div className="flex justify-between font-bold">
          <span>Total</span>
          <span>{money(sale.grand_total)}</span>
        </div>
        <div className="flex justify-between">
          <span>Paid</span>
          <span>{money(sale.paid_total)}</span>
        </div>
        <div className="flex justify-between">
          <span>Change</span>
          <span>{money(sale.change_due)}</span>
        </div>
      </div>
    </div>
  );
}
