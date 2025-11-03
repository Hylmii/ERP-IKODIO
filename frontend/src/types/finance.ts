import { AuditFields } from './common'

// ============ Enums ============

export enum InvoiceType {
  SALES = 'sales',
  PURCHASE = 'purchase',
  PROFORMA = 'proforma',
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  PARTIAL = 'partial',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
}

export enum PaymentType {
  RECEIPT = 'receipt',
  PAYMENT = 'payment',
}

export enum PaymentMethod {
  CASH = 'cash',
  BANK_TRANSFER = 'bank_transfer',
  CHECK = 'check',
  CREDIT_CARD = 'credit_card',
  OTHER = 'other',
}

export enum PaymentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum ExpenseStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
}

export enum ExpenseCategory {
  OPERATIONAL = 'operational',
  TRAVEL = 'travel',
  OFFICE = 'office',
  UTILITIES = 'utilities',
  SALARIES = 'salaries',
  MARKETING = 'marketing',
  TRAINING = 'training',
  OTHER = 'other',
}

export enum BudgetStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  ACTIVE = 'active',
  CLOSED = 'closed',
}

export enum AccountType {
  ASSET = 'asset',
  LIABILITY = 'liability',
  EQUITY = 'equity',
  REVENUE = 'revenue',
  EXPENSE = 'expense',
}

export enum TransactionType {
  DEBIT = 'debit',
  CREDIT = 'credit',
}

export enum TaxType {
  PPH21 = 'pph21',
  PPH23 = 'pph23',
  PPH25 = 'pph25',
  PPN = 'ppn',
  OTHER = 'other',
}

export enum CashFlowType {
  OPERATING = 'operating',
  INVESTING = 'investing',
  FINANCING = 'financing',
}

// ============ Invoice Types ============

export interface InvoiceLine {
  id?: string
  description: string
  quantity: number
  unit_price: number
  discount_percentage?: number
  tax_percentage?: number
  amount: number
  line_number?: number
}

export interface Invoice extends AuditFields {
  id: string
  invoice_number: string
  invoice_type: string
  invoice_date: string
  due_date: string
  
  // Client info
  client: number
  client_name?: string
  client_email?: string
  
  // Project reference
  project?: number
  project_name?: string
  
  // Amounts
  subtotal: number
  tax_amount: number
  discount_amount: number
  total_amount: number
  paid_amount: number
  outstanding_amount: number
  
  currency: string
  
  // Tax
  tax_percentage: number
  tax_number?: string
  
  // Status
  status: string
  
  // Terms & Notes
  payment_terms?: string
  notes?: string
  internal_notes?: string
  
  // Lines
  lines?: InvoiceLine[]
  
  // Documents
  invoice_file?: string
  
  // Computed
  is_overdue?: boolean
  days_overdue?: number
}

export interface InvoiceFormData {
  invoice_type: string
  invoice_date: string
  due_date: string
  client: number
  project?: number
  tax_percentage: number
  discount_amount?: number
  payment_terms?: string
  notes?: string
  internal_notes?: string
  lines: InvoiceLine[]
}

// ============ Payment Types ============

export interface Payment extends AuditFields {
  id: string
  payment_number: string
  payment_type: string
  payment_date: string
  
  // Party
  client?: number
  client_name?: string
  
  // Invoice reference
  invoice?: number
  invoice_number?: string
  
  // Amount
  amount: number
  currency: string
  
  // Payment details
  payment_method: string
  reference_number?: string
  bank_name?: string
  bank_account?: string
  
  status: string
  
  // Account
  account: number
  account_name?: string
  
  notes?: string
  attachments?: Record<string, unknown>
}

export interface PaymentFormData {
  payment_type: string
  payment_date: string
  client?: number
  invoice?: number
  amount: number
  payment_method: string
  reference_number?: string
  bank_name?: string
  bank_account?: string
  account: number
  notes?: string
}

// ============ Expense Types ============

export interface Expense extends AuditFields {
  id: string
  expense_number: string
  expense_date: string
  
  // Requester
  employee: number
  employee_name?: string
  
  // Details
  category: string
  description: string
  amount: number
  currency: string
  
  // Allocation
  project?: number
  project_name?: string
  department?: number
  department_name?: string
  
  // Account
  account: number
  account_name?: string
  
  // Status & Approval
  status: string
  approved_by?: number
  approved_by_name?: string
  approved_at?: string
  approval_notes?: string
  
  // Payment
  paid_at?: string
  payment_reference?: string
  
  // Attachments
  attachments?: Record<string, unknown>
}

export interface ExpenseFormData {
  expense_date: string
  category: string
  description: string
  amount: number
  project?: number
  department?: number
  account: number
  attachments?: File[]
}

// ============ Budget Types ============

export interface BudgetLine {
  id?: string
  account: number
  account_code?: string
  account_name?: string
  allocated_amount: number
  spent_amount?: number
  committed_amount?: number
  remaining_amount?: number
  notes?: string
}

export interface Budget extends AuditFields {
  id: string
  name: string
  description: string
  
  // Period
  fiscal_year: number
  period_start: string
  period_end: string
  start_date: string
  end_date: string
  
  // Allocation
  department?: number
  department_name?: string
  project?: number
  project_name?: string
  
  // Amounts
  total_budget: number
  total_allocated: number
  total_spent: number
  total_committed: number
  total_remaining?: number
  remaining_budget: number
  utilization_percentage?: number | string
  
  currency: string
  status: string
  
  // Approval
  approved_by?: number
  approved_by_name?: string
  approved_at?: string
  
  // Lines
  lines?: BudgetLine[]
  notes?: string
}

export interface BudgetFormData {
  name: string
  description: string
  fiscal_year: number
  start_date: string
  end_date: string
  department?: number
  project?: number
  lines: BudgetLine[]
}

// ============ Bank Account Types ============

export interface BankAccount extends AuditFields {
  id: string
  account_name: string
  bank_name: string
  account_number: string
  account_type: string
  
  currency: string
  current_balance: number
  
  // Bank details
  branch?: string
  swift_code?: string
  iban?: string
  
  account_holder_name: string
  
  // GL mapping
  gl_account: number
  gl_account_name?: string
  
  status: string
  
  // API integration
  api_enabled: boolean
  last_sync?: string
  
  notes?: string
}

// ============ General Ledger Types ============

export interface GeneralLedger extends AuditFields {
  id: string
  code: string
  name: string
  description?: string
  account_type: string
  
  parent?: number
  parent_name?: string
  
  is_active: boolean
  is_header: boolean
  
  currency: string
  balance: number
  
  sub_accounts?: GeneralLedger[]
  sub_account_count?: number
  transaction_count?: number
}

// ============ Transaction Types ============

export interface Transaction {
  id: string
  date: string
  transaction_date: string
  description: string
  account: number
  account_name?: string
  transaction_type: 'debit' | 'credit'
  debit: number
  credit: number
  amount: number
  balance: number
  reference?: string
}

// ============ Tax Types ============

export interface Tax extends AuditFields {
  id: string
  tax_number: string
  tax_type: string
  tax_period_month: number
  tax_period_year: number
  
  taxable_amount: number
  tax_rate: number
  tax_amount: number
  
  status: string
  
  filing_date?: string
  payment_date?: string
  reference_number?: string
  
  tax_report?: string
  notes?: string
}

// ============ Report Types ============

export interface FinancialSummary {
  total_revenue: number
  total_expenses: number
  net_profit: number
  profit_margin: number
  
  total_assets: number
  total_liabilities: number
  equity: number
  
  cash_inflow: number
  cash_outflow: number
  net_cash_flow: number
  
  outstanding_invoices: number
  overdue_invoices: number
  pending_expenses: number
  
  budget_utilization: number
}

export interface RevenueExpenseData {
  month: string
  revenue: number
  expense: number
  profit: number
}

export interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
  color?: string
}

export interface CashFlowData {
  date: string
  operating: number
  investing: number
  financing: number
  total: number
}

export interface ProfitLossReport {
  period_start: string
  period_end: string
  
  revenue: {
    sales: number
    services: number
    other: number
    total: number
  }
  
  cost_of_goods_sold: number
  gross_profit: number
  gross_margin: number
  
  operating_expenses: {
    salaries: number
    rent: number
    utilities: number
    marketing: number
    other: number
    total: number
  }
  
  operating_profit: number
  operating_margin: number
  
  other_income: number
  other_expenses: number
  
  profit_before_tax: number
  tax: number
  net_profit: number
  net_margin: number
}

export interface BalanceSheet {
  as_of_date: string
  
  assets: {
    current_assets: {
      cash: number
      accounts_receivable: number
      inventory: number
      other: number
      total: number
    }
    fixed_assets: {
      property: number
      equipment: number
      vehicles: number
      accumulated_depreciation: number
      total: number
    }
    total: number
  }
  
  liabilities: {
    current_liabilities: {
      accounts_payable: number
      short_term_loans: number
      other: number
      total: number
    }
    long_term_liabilities: {
      long_term_loans: number
      other: number
      total: number
    }
    total: number
  }
  
  equity: {
    capital: number
    retained_earnings: number
    current_year_profit: number
    total: number
  }
  
  total_liabilities_equity: number
}

export interface CashFlowStatement {
  period_start: string
  period_end: string
  
  operating_activities: {
    net_profit: number
    depreciation: number
    accounts_receivable_change: number
    accounts_payable_change: number
    inventory_change: number
    other: number
    total: number
  }
  
  investing_activities: {
    equipment_purchase: number
    equipment_sale: number
    investment_purchase: number
    investment_sale: number
    other: number
    total: number
  }
  
  financing_activities: {
    loan_received: number
    loan_repayment: number
    capital_injection: number
    dividends_paid: number
    other: number
    total: number
  }
  
  net_cash_flow: number
  opening_cash: number
  closing_cash: number
}

// ============ Dashboard Types ============

export interface FinanceDashboardData {
  summary: FinancialSummary & {
    cash_balance: number
  }
  revenue_expense_trend: RevenueExpenseData[]
  expense_by_category: CategoryBreakdown[]
  recent_invoices: Invoice[]
  recent_expenses: Expense[]
  recent_payments: Payment[]
  recent_transactions: Transaction[]
  cash_flow_trend: CashFlowData[]
  invoices: {
    total_outstanding: number
    outstanding_amount: number
    overdue_count: number
    overdue_amount: number
  }
  expenses: {
    pending_count: number
    pending_amount: number
  }
  budget_summary: Budget[]
  budget_status: {
    department: string
    allocated: number
    spent: number
    percentage: number
  }[]
}

// ============ Filter & Query Types ============

export interface InvoiceFilters {
  status?: string
  invoice_type?: string
  client?: number
  project?: number
  date_from?: string
  date_to?: string
  search?: string
}

export interface ExpenseFilters {
  status?: string
  category?: string
  employee?: number
  department?: number
  project?: number
  date_from?: string
  date_to?: string
  search?: string
}

export interface PaymentFilters {
  payment_type?: string
  payment_method?: string
  status?: string
  client?: number
  date_from?: string
  date_to?: string
  search?: string
}

export interface TransactionFilters {
  account?: number
  date_from?: string
  date_to?: string
  transaction_type?: string
  search?: string
}
