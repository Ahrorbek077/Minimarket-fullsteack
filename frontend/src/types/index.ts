// ─── Auth ─────────────────────────────────────────────────────────────────────
export type UserRole =
  | "super_admin" | "admin" | "cashier" | "storekeeper" | "accountant";

export type UserLanguage = "uz" | "uz_cryl" | "ru" | "en";

export interface User {
  id:               number;
  email:            string;
  full_name:        string;
  phone:            string;
  avatar:           string | null;
  role:             UserRole;
  role_display:     string;
  language:         UserLanguage;
  language_display: string;
  date_joined:      string;
}

export interface AuthTokens {
  access:  string;
  refresh: string;
  user:    User;
}

// ─── Product ──────────────────────────────────────────────────────────────────
export interface Category {
  id:           number;
  name:         string;
  icon:         string;
  parent:       number | null;
  parent_name:  string | null;
  children:     Category[];
  product_count:number;
}

export interface Unit {
  id:         number;
  name:       string;
  short_name: string;
}

export interface Product {
  id:             number;
  name:           string;
  barcode:        string | null;
  category_name:  string | null;
  unit_short:     string | null;
  cost_price:     string;
  sell_price:     string;
  profit_margin:  number;
  stock_qty:      number;
  is_low_stock:   boolean;
  is_active:      boolean;
  image:          string | null;
}

// ─── Cart ─────────────────────────────────────────────────────────────────────
export interface CartItem {
  product_id: number;
  name:       string;
  barcode:    string;
  sell_price: string;
  quantity:   string;
  unit_short: string;
  subtotal:   string;
}

export interface Cart {
  items:        CartItem[];
  item_count:   number;
  total_amount: string;
}

// ─── Sale ─────────────────────────────────────────────────────────────────────
export type PaymentMethod = "cash" | "card" | "debt";
export type SaleStatus    = "completed" | "returned" | "partial";

export interface PaymentInput {
  method: PaymentMethod;
  amount: string;
}

export interface Sale {
  id:              number;
  invoice_no:      string;
  status:          SaleStatus;
  status_display:  string;
  total_amount:    string;
  discount_pct:    string;
  discount_amount: string;
  net_amount:      string;
  paid_amount:     string;
  debt_amount:     string;
  cashier_name:    string | null;
  payment_methods: PaymentMethod[];
  created_at:      string;
}

// ─── Purchase ─────────────────────────────────────────────────────────────────
export type PurchaseStatus =
  | "draft" | "received" | "partial" | "paid" | "cancelled";

export interface Purchase {
  id:            number;
  company_name:  string;
  branch_name:   string | null;
  invoice_no:    string;
  status:        PurchaseStatus;
  status_display:string;
  total_amount:  string;
  paid_amount:   string;
  debt_amount:   string;
  due_date:      string | null;
  is_overdue:    boolean;
  created_by_name: string | null;
  created_at:    string;
}

// ─── Company ──────────────────────────────────────────────────────────────────
export interface Company {
  id:           number;
  name:         string;
  phone:        string;
  address:      string;
  inn:          string;
  branch_count: number;
  created_at:   string;
}

export interface Branch {
  id:        number;
  name:      string;
  phone:     string;
  address:   string;
  created_at:string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
export interface PeriodStats {
  period:       string;
  date_from:    string;
  date_to:      string;
  sales_count:  number;
  revenue:      string;
  gross_profit: string;
  discount:     string;
  debt:         string;
  cash:         string;
  card:         string;
  debt_payments:string;
}

export interface StockOverview {
  total_products:  number;
  low_stock_count: number;
  out_of_stock:    number;
  cost_value:      string;
  sell_value:      string;
}

export interface DebtsOverview {
  count:         number;
  total_debt:    string;
  overdue_count: number;
  overdue_debt:  string;
}

export interface SalesChartPoint {
  date:    string;
  count:   number;
  revenue: string;
}

export interface DashboardData {
  today:        PeriodStats;
  week:         PeriodStats;
  month:        PeriodStats;
  year:         PeriodStats;
  stock:        StockOverview;
  debts:        DebtsOverview;
  top_products: { product__id: number; product__name: string; total_qty: string; total_revenue: string }[];
  sales_chart:  SalesChartPoint[];
  recent_sales: { id: number; invoice_no: string; net_amount: string; created_at: string; cashier__full_name: string | null }[];
  low_stock:    { product__id: number; product__name: string; quantity: string; product__min_stock: string }[];
}

// ─── Pagination ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count:        number;
  total_pages:  number;
  current_page: number;
  page_size:    number;
  next:         string | null;
  previous:     string | null;
  results:      T[];
}

// ─── API Response ─────────────────────────────────────────────────────────────
export interface ApiSuccess<T> {
  success: true;
  data:    T;
  message?: string;
}

export interface ApiError {
  success: false;
  error: {
    code:    string;
    message: string;
    details: Record<string, string[]> | null;
  };
}
