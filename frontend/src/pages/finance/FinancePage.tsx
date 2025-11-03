import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import financeService from '@/services/financeService'
import type { FinanceDashboardData } from '@/types/finance'

export default function FinancePage() {
  const [dashboard, setDashboard] = useState<FinanceDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await financeService.getDashboard()
      setDashboard(data)
    } catch (err) {
      console.error('Error fetching dashboard:', err)
      // Set default empty data instead of error
      setDashboard({
        summary: {
          total_revenue: 0,
          total_expenses: 0,
          net_profit: 0,
          profit_margin: 0,
          total_assets: 0,
          total_liabilities: 0,
          equity: 0,
          cash_inflow: 0,
          cash_outflow: 0,
          net_cash_flow: 0,
          outstanding_invoices: 0,
          overdue_invoices: 0,
          pending_expenses: 0,
          budget_utilization: 0,
          cash_balance: 0,
        },
        revenue_expense_trend: [],
        expense_by_category: [],
        recent_invoices: [],
        recent_expenses: [],
        recent_payments: [],
        recent_transactions: [],
        cash_flow_trend: [],
        invoices: {
          total_outstanding: 0,
          outstanding_amount: 0,
          overdue_count: 0,
          overdue_amount: 0,
        },
        expenses: {
          pending_count: 0,
          pending_amount: 0,
        },
        budget_summary: [],
        budget_status: [],
      })
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number | string) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(num)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No dashboard data available</div>
      </div>
    )
  }

  const summary = dashboard?.summary || {
    total_revenue: 0,
    total_expenses: 0,
    net_profit: 0,
    profit_margin: 0,
    total_assets: 0,
    total_liabilities: 0,
    equity: 0,
    cash_inflow: 0,
    cash_outflow: 0,
    net_cash_flow: 0,
    outstanding_invoices: 0,
    overdue_invoices: 0,
    pending_expenses: 0,
    budget_utilization: 0,
    cash_balance: 0,
  }
  
  const profitMargin = summary.total_revenue > 0 
    ? ((summary.total_revenue - summary.total_expenses) / summary.total_revenue * 100).toFixed(1)
    : 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Finance Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Financial overview and key metrics</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/finance/reports"
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            📊 Reports
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-500">Total Revenue</div>
            <span className="text-green-600">↑</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(summary.total_revenue)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Year to date</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-500">Total Expenses</div>
            <span className="text-red-600">↓</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(summary.total_expenses)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Year to date</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-500">Net Profit</div>
            <span className={`${summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {summary.net_profit >= 0 ? '↑' : '↓'}
            </span>
          </div>
          <div className={`text-2xl font-bold ${summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(summary.net_profit)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Margin: {profitMargin}%</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-500">Cash Balance</div>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {formatCurrency(summary.cash_balance)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Available funds</div>
        </div>
      </div>

      {/* Invoice & Payment Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-2">Outstanding Invoices</div>
          <div className="text-3xl font-bold text-orange-600">
            {dashboard?.invoices?.total_outstanding ?? 0}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {formatCurrency(dashboard?.invoices?.outstanding_amount ?? 0)}
          </div>
          <Link
            to="/finance/invoices?status=sent,overdue"
            className="text-sm text-blue-600 hover:text-blue-800 mt-2 inline-block"
          >
            View invoices →
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-2">Overdue Invoices</div>
          <div className="text-3xl font-bold text-red-600">
            {dashboard?.invoices?.overdue_count ?? 0}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {formatCurrency(dashboard?.invoices?.overdue_amount ?? 0)}
          </div>
          <Link
            to="/finance/invoices?status=overdue"
            className="text-sm text-blue-600 hover:text-blue-800 mt-2 inline-block"
          >
            View overdue →
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-2">Pending Expenses</div>
          <div className="text-3xl font-bold text-yellow-600">
            {dashboard?.expenses?.pending_count ?? 0}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {formatCurrency(dashboard?.expenses?.pending_amount ?? 0)}
          </div>
          <Link
            to="/finance/expenses?status=pending"
            className="text-sm text-blue-600 hover:text-blue-800 mt-2 inline-block"
          >
            Review expenses →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
          </div>
          <div className="p-6">
            {dashboard.recent_transactions && dashboard.recent_transactions.length > 0 ? (
              <div className="space-y-3">
                {dashboard.recent_transactions.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-sm text-gray-900">{tx.description}</p>
                      <p className="text-xs text-gray-500">{formatDate(tx.transaction_date)}</p>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold text-sm ${
                        tx.transaction_type === 'debit' ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {tx.transaction_type === 'debit' ? '-' : '+'}{formatCurrency(tx.amount)}
                      </p>
                      <p className="text-xs text-gray-500">{tx.account_name}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">No recent transactions</div>
            )}
          </div>
        </div>

        {/* Budget Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Budget Overview</h2>
          </div>
          <div className="p-6">
            {dashboard.budget_summary && dashboard.budget_summary.length > 0 ? (
              <div className="space-y-4">
                {dashboard.budget_summary.map((budget) => {
                  const percentage = Number(budget.utilization_percentage)
                  const color = percentage > 90 ? 'bg-red-600' : percentage > 70 ? 'bg-yellow-600' : 'bg-green-600'
                  
                  return (
                    <div key={budget.id}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-900">{budget.name}</span>
                        <span className="text-sm text-gray-600">
                          {formatCurrency(budget.total_spent)} / {formatCurrency(budget.total_allocated)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${color}`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-500">{percentage.toFixed(1)}% used</span>
                        <span className={`text-xs font-medium ${
                          Number(budget.remaining_budget) > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(budget.remaining_budget)} remaining
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">No budget data available</div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link
          to="/finance/invoices/new"
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="text-3xl mb-2">📄</div>
          <div className="font-semibold text-gray-900">Create Invoice</div>
          <div className="text-sm text-gray-500 mt-1">Issue new invoice</div>
        </Link>

        <Link
          to="/finance/expenses"
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="text-3xl mb-2">💰</div>
          <div className="font-semibold text-gray-900">Submit Expense</div>
          <div className="text-sm text-gray-500 mt-1">Record new expense</div>
        </Link>

        <Link
          to="/finance/payments"
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="text-3xl mb-2">💳</div>
          <div className="font-semibold text-gray-900">Record Payment</div>
          <div className="text-sm text-gray-500 mt-1">Log transaction</div>
        </Link>

        <Link
          to="/finance/reports"
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="text-3xl mb-2">📊</div>
          <div className="font-semibold text-gray-900">View Reports</div>
          <div className="text-sm text-gray-500 mt-1">Financial statements</div>
        </Link>
      </div>
    </div>
  )
}
