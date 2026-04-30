export type Role = "ADMIN" | "CASHIER";
export type PaymentMode = "CASH" | "UPI" | "CARD";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  default_gst_rate: string;
  is_active: boolean;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  barcode: string | null;
  category_id: number | null;
  category_name?: string | null;
  selling_price: string;
  cost_price: string;
  gst_rate: string;
  unit: string;
  is_active: boolean;
  on_hand: string;
  reorder_level: string;
}

export interface Customer {
  id: number;
  name: string;
  phone: string | null;
  email: string | null;
  address: string | null;
  loyalty_points: number;
  is_active: boolean;
}

export interface Supplier {
  id: number;
  name: string;
  contact_name: string | null;
  phone: string | null;
  email: string | null;
  gstin: string | null;
  address: string | null;
  is_active: boolean;
}

export interface InventoryBatch {
  id: number;
  product_id: number;
  batch_number: string;
  expiry_date: string | null;
  cost_price: string;
  received_quantity: string;
  quantity_on_hand: string;
}

export interface InventoryRow {
  product_id: number;
  product_name: string;
  sku: string;
  barcode: string | null;
  on_hand: string;
  reorder_level: string;
  is_low_stock: boolean;
  batches: InventoryBatch[];
}

export interface SaleItem {
  id: number;
  product_id: number;
  product_name: string;
  sku: string;
  barcode: string | null;
  quantity: string;
  returned_quantity: string;
  unit_price: string;
  discount_amount: string;
  gst_rate: string;
  taxable_amount: string;
  tax_amount: string;
  line_total: string;
}

export interface Sale {
  id: number;
  invoice_number: string;
  cashier_id: number;
  customer_id: number | null;
  shift_id: number | null;
  status: string;
  subtotal: string;
  discount_total: string;
  taxable_total: string;
  tax_total: string;
  grand_total: string;
  paid_total: string;
  change_due: string;
  notes: string | null;
  created_at: string;
  items: SaleItem[];
  payments: { id: number; mode: PaymentMode; amount: string; reference: string | null }[];
}

export interface SaleListRow {
  id: number;
  invoice_number: string;
  status: string;
  cashier_name: string;
  customer_name: string | null;
  grand_total: string;
  paid_total: string;
  created_at: string;
}

export interface Shift {
  id: number;
  cashier_id: number;
  status: "OPEN" | "CLOSED";
  opened_at: string;
  closed_at: string | null;
  opening_cash: string;
  closing_cash: string | null;
  expected_cash: string | null;
  variance: string | null;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_name?: string;
  supplier_id?: number;
  status: string;
  grand_total: string;
  expected_date: string | null;
  created_at: string;
  items?: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: number;
  product_id: number;
  quantity_ordered: string;
  quantity_received: string;
  unit_cost: string;
  gst_rate: string;
  line_total: string;
}

export interface DashboardMetrics {
  today_revenue: string;
  month_revenue: string;
  today_sales_count: number;
  low_stock_count: number;
  open_purchase_orders: number;
  active_customers: number;
}
