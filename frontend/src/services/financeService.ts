import api from './api'
import type {
  Invoice,
  InvoiceFormData,
  InvoiceFilters,
  Payment,
  PaymentFormData,
  PaymentFilters,
  Expense,
  ExpenseFormData,
  ExpenseFilters,
  Budget,
  BudgetFormData,
  BankAccount,
  GeneralLedger,
  Transaction,
  TransactionFilters,
  Tax,
  FinanceDashboardData,
  ProfitLossReport,
  BalanceSheet,
  CashFlowStatement,
  FinancialSummary,
} from '@/types/finance'
import type { PaginatedResponse } from '@/types/common'

// ============ Dashboard ============

export const financeService = {
  // Dashboard
  getDashboard: async (): Promise<FinanceDashboardData> => {
    const response = await api.get<FinanceDashboardData>('/finance/dashboard/')
    return response.data
  },

  getFinancialSummary: async (
    startDate?: string,
    endDate?: string
  ): Promise<FinancialSummary> => {
    const response = await api.get<FinancialSummary>('/finance/summary/', {
      params: { start_date: startDate, end_date: endDate },
    })
    return response.data
  },

  // ============ Invoices ============

  getInvoices: async (params?: InvoiceFilters & {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Invoice>> => {
    const response = await api.get<PaginatedResponse<Invoice>>('/finance/invoices/', {
      params,
    })
    return response.data
  },

  getInvoice: async (id: string): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/finance/invoices/${id}/`)
    return response.data
  },

  createInvoice: async (data: InvoiceFormData): Promise<Invoice> => {
    const response = await api.post<Invoice>('/finance/invoices/', data)
    return response.data
  },

  updateInvoice: async (id: string, data: Partial<InvoiceFormData>): Promise<Invoice> => {
    const response = await api.patch<Invoice>(`/finance/invoices/${id}/`, data)
    return response.data
  },

  deleteInvoice: async (id: string): Promise<void> => {
    await api.delete(`/finance/invoices/${id}/`)
  },

  // Invoice actions
  sendInvoice: async (id: string, email?: string): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/finance/invoices/${id}/send/`, {
      email,
    })
    return response.data
  },

  markInvoicePaid: async (id: string, paymentData: {
    payment_date: string
    payment_method: string
    reference_number?: string
    notes?: string
  }): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/finance/invoices/${id}/mark-paid/`, paymentData)
    return response.data
  },

  cancelInvoice: async (id: string, reason?: string): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/finance/invoices/${id}/cancel/`, {
      reason,
    })
    return response.data
  },

  duplicateInvoice: async (id: string): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/finance/invoices/${id}/duplicate/`)
    return response.data
  },

  downloadInvoicePDF: async (id: string): Promise<Blob> => {
    const response = await api.get(`/finance/invoices/${id}/pdf/`, {
      responseType: 'blob',
    })
    return response.data
  },

  // ============ Payments ============

  getPayments: async (params?: PaymentFilters & {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Payment>> => {
    const response = await api.get<PaginatedResponse<Payment>>('/finance/payments/', {
      params,
    })
    return response.data
  },

  getPayment: async (id: string): Promise<Payment> => {
    const response = await api.get<Payment>(`/finance/payments/${id}/`)
    return response.data
  },

  createPayment: async (data: PaymentFormData): Promise<Payment> => {
    const response = await api.post<Payment>('/finance/payments/', data)
    return response.data
  },

  updatePayment: async (id: string, data: Partial<PaymentFormData>): Promise<Payment> => {
    const response = await api.patch<Payment>(`/finance/payments/${id}/`, data)
    return response.data
  },

  deletePayment: async (id: string): Promise<void> => {
    await api.delete(`/finance/payments/${id}/`)
  },

  confirmPayment: async (id: string): Promise<Payment> => {
    const response = await api.post<Payment>(`/finance/payments/${id}/confirm/`)
    return response.data
  },

  // ============ Expenses ============

  getExpenses: async (params?: ExpenseFilters & {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Expense>> => {
    const response = await api.get<PaginatedResponse<Expense>>('/finance/expenses/', {
      params,
    })
    return response.data
  },

  getExpense: async (id: string): Promise<Expense> => {
    const response = await api.get<Expense>(`/finance/expenses/${id}/`)
    return response.data
  },

  createExpense: async (data: ExpenseFormData): Promise<Expense> => {
    const formData = new FormData()
    
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'attachments' && Array.isArray(value)) {
        value.forEach((file) => {
          formData.append('attachments', file)
        })
      } else if (value !== undefined && value !== null) {
        formData.append(key, String(value))
      }
    })

    const response = await api.post<Expense>('/finance/expenses/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  updateExpense: async (id: string, data: Partial<ExpenseFormData>): Promise<Expense> => {
    const response = await api.patch<Expense>(`/finance/expenses/${id}/`, data)
    return response.data
  },

  deleteExpense: async (id: string): Promise<void> => {
    await api.delete(`/finance/expenses/${id}/`)
  },

  // Expense actions
  submitExpense: async (id: string): Promise<Expense> => {
    const response = await api.post<Expense>(`/finance/expenses/${id}/submit/`)
    return response.data
  },

  approveExpense: async (id: string, notes?: string): Promise<Expense> => {
    const response = await api.post<Expense>(`/finance/expenses/${id}/approve/`, {
      approval_notes: notes,
    })
    return response.data
  },

  rejectExpense: async (id: string, reason: string): Promise<Expense> => {
    const response = await api.post<Expense>(`/finance/expenses/${id}/reject/`, {
      approval_notes: reason,
    })
    return response.data
  },

  // ============ Budgets ============

  getBudgets: async (params?: {
    fiscal_year?: number
    department?: number
    project?: number
    status?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Budget>> => {
    const response = await api.get<PaginatedResponse<Budget>>('/finance/budgets/', {
      params,
    })
    return response.data
  },

  getBudget: async (id: string): Promise<Budget> => {
    const response = await api.get<Budget>(`/finance/budgets/${id}/`)
    return response.data
  },

  createBudget: async (data: BudgetFormData): Promise<Budget> => {
    const response = await api.post<Budget>('/finance/budgets/', data)
    return response.data
  },

  updateBudget: async (id: string, data: Partial<BudgetFormData>): Promise<Budget> => {
    const response = await api.patch<Budget>(`/finance/budgets/${id}/`, data)
    return response.data
  },

  deleteBudget: async (id: string): Promise<void> => {
    await api.delete(`/finance/budgets/${id}/`)
  },

  approveBudget: async (id: string): Promise<Budget> => {
    const response = await api.post<Budget>(`/finance/budgets/${id}/approve/`)
    return response.data
  },

  activateBudget: async (id: string): Promise<Budget> => {
    const response = await api.post<Budget>(`/finance/budgets/${id}/activate/`)
    return response.data
  },

  closeBudget: async (id: string): Promise<Budget> => {
    const response = await api.post<Budget>(`/finance/budgets/${id}/close/`)
    return response.data
  },

  // ============ Bank Accounts ============

  getBankAccounts: async (): Promise<BankAccount[]> => {
    const response = await api.get<BankAccount[]>('/finance/bank-accounts/')
    return response.data
  },

  getBankAccount: async (id: string): Promise<BankAccount> => {
    const response = await api.get<BankAccount>(`/finance/bank-accounts/${id}/`)
    return response.data
  },

  createBankAccount: async (data: Partial<BankAccount>): Promise<BankAccount> => {
    const response = await api.post<BankAccount>('/finance/bank-accounts/', data)
    return response.data
  },

  updateBankAccount: async (id: string, data: Partial<BankAccount>): Promise<BankAccount> => {
    const response = await api.patch<BankAccount>(`/finance/bank-accounts/${id}/`, data)
    return response.data
  },

  deleteBankAccount: async (id: string): Promise<void> => {
    await api.delete(`/finance/bank-accounts/${id}/`)
  },

  syncBankAccount: async (id: string): Promise<BankAccount> => {
    const response = await api.post<BankAccount>(`/finance/bank-accounts/${id}/sync/`)
    return response.data
  },

  // ============ General Ledger ============

  getGLAccounts: async (params?: {
    account_type?: string
    is_active?: boolean
    search?: string
  }): Promise<GeneralLedger[]> => {
    const response = await api.get<GeneralLedger[]>('/finance/accounts/', {
      params,
    })
    return response.data
  },

  getGLAccount: async (id: string): Promise<GeneralLedger> => {
    const response = await api.get<GeneralLedger>(`/finance/accounts/${id}/`)
    return response.data
  },

  // ============ Transactions ============

  getTransactions: async (params?: TransactionFilters & {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Transaction>> => {
    const response = await api.get<PaginatedResponse<Transaction>>('/finance/transactions/', {
      params,
    })
    return response.data
  },

  getAccountTransactions: async (accountId: string, params?: {
    date_from?: string
    date_to?: string
  }): Promise<Transaction[]> => {
    const response = await api.get<Transaction[]>(`/finance/accounts/${accountId}/transactions/`, {
      params,
    })
    return response.data
  },

  // ============ Taxes ============

  getTaxes: async (params?: {
    tax_type?: string
    tax_period_year?: number
    tax_period_month?: number
    status?: string
  }): Promise<Tax[]> => {
    const response = await api.get<Tax[]>('/finance/taxes/', {
      params,
    })
    return response.data
  },

  getTax: async (id: string): Promise<Tax> => {
    const response = await api.get<Tax>(`/finance/taxes/${id}/`)
    return response.data
  },

  calculateTax: async (data: {
    tax_type: string
    period_month: number
    period_year: number
  }): Promise<Tax> => {
    const response = await api.post<Tax>('/finance/taxes/calculate/', data)
    return response.data
  },

  fileTax: async (id: string): Promise<Tax> => {
    const response = await api.post<Tax>(`/finance/taxes/${id}/file/`)
    return response.data
  },

  // ============ Reports ============

  getProfitLossReport: async (params: {
    start_date: string
    end_date: string
    department?: number
    project?: number
  }): Promise<ProfitLossReport> => {
    const response = await api.get<ProfitLossReport>('/finance/reports/profit-loss/', {
      params,
    })
    return response.data
  },

  getBalanceSheet: async (params: {
    as_of_date: string
  }): Promise<BalanceSheet> => {
    const response = await api.get<BalanceSheet>('/finance/reports/balance-sheet/', {
      params,
    })
    return response.data
  },

  getCashFlowStatement: async (params: {
    start_date: string
    end_date: string
  }): Promise<CashFlowStatement> => {
    const response = await api.get<CashFlowStatement>('/finance/reports/cash-flow/', {
      params,
    })
    return response.data
  },

  getRevenueExpenseTrend: async (params: {
    start_date: string
    end_date: string
    group_by?: 'day' | 'week' | 'month' | 'quarter'
  }): Promise<{ month: string; revenue: number; expense: number; profit: number }[]> => {
    const response = await api.get('/finance/reports/revenue-expense-trend/', {
      params,
    })
    return response.data
  },

  getExpenseByCategory: async (params: {
    start_date: string
    end_date: string
  }): Promise<{ category: string; amount: number; percentage: number }[]> => {
    const response = await api.get('/finance/reports/expense-by-category/', {
      params,
    })
    return response.data
  },

  // Export reports
  exportReport: async (reportType: string, params: Record<string, unknown>, format: 'pdf' | 'excel' = 'pdf'): Promise<Blob> => {
    const response = await api.get(`/finance/reports/${reportType}/export/`, {
      params: { ...params, format },
      responseType: 'blob',
    })
    return response.data
  },
}

export default financeService
