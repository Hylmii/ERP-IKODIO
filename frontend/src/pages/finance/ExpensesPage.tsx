import { useState, useEffect, useCallback } from 'react'
import financeService from '@/services/financeService'
import type { Expense, ExpenseFilters } from '@/types/finance'

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [filters, setFilters] = useState<ExpenseFilters>({
    search: '',
    status: undefined,
    category: undefined,
    date_from: undefined,
    date_to: undefined,
  })
  
  const [currentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const pageSize = 20

  const [stats, setStats] = useState({
    pending: 0,
    approved: 0,
    rejected: 0,
    total_pending_amount: 0,
    total_approved_amount: 0,
  })

  const fetchExpenses = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await financeService.getExpenses({
        ...filters,
        page: currentPage,
        page_size: pageSize,
      })
      
      setExpenses(response.results)
      setTotalCount(response.count)
      // setTotalPages(Math.ceil(response.count / pageSize))
      
      const allExpenses = response.results
      setStats({
        pending: allExpenses.filter(exp => exp.status === 'pending').length,
        approved: allExpenses.filter(exp => exp.status === 'approved').length,
        rejected: allExpenses.filter(exp => exp.status === 'rejected').length,
        total_pending_amount: allExpenses
          .filter(exp => exp.status === 'pending')
          .reduce((sum, exp) => sum + Number(exp.amount), 0),
        total_approved_amount: allExpenses
          .filter(exp => exp.status === 'approved')
          .reduce((sum, exp) => sum + Number(exp.amount), 0),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch expenses')
      console.error('Error fetching expenses:', err)
    } finally {
      setLoading(false)
    }
  }, [currentPage, filters])

  useEffect(() => {
    fetchExpenses()
  }, [fetchExpenses])

  const approveExpense = async (id: string) => {
    const notes = prompt('Approval notes (optional):')
    try {
      await financeService.approveExpense(id, notes || undefined)
      alert('Expense approved!')
      fetchExpenses()
    } catch (err) {
      alert('Failed to approve: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const rejectExpense = async (id: string) => {
    const reason = prompt('Rejection reason:')
    if (!reason) return
    
    try {
      await financeService.rejectExpense(id, reason)
      alert('Expense rejected!')
      fetchExpenses()
    } catch (err) {
      alert('Failed to reject: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
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
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading && expenses.length === 0) {
    return <div className="flex items-center justify-center h-64"><div className="text-gray-500">Loading expenses...</div></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Expenses</h1>
          <p className="text-sm text-gray-500 mt-1">Manage and approve company expenses</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + Submit Expense
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Pending Approval</div>
          <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          <div className="text-sm text-gray-500 mt-1">{formatCurrency(stats.total_pending_amount)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Approved</div>
          <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
          <div className="text-sm text-gray-500 mt-1">{formatCurrency(stats.total_approved_amount)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Rejected</div>
          <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Expenses</div>
          <div className="text-2xl font-bold text-gray-900">{totalCount}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="Search description..."
            value={filters.search || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <select
            value={filters.status || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          <select
            value={filters.category || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            <option value="travel">Travel</option>
            <option value="meals">Meals & Entertainment</option>
            <option value="supplies">Office Supplies</option>
            <option value="utilities">Utilities</option>
            <option value="marketing">Marketing</option>
            <option value="other">Other</option>
          </select>

          <input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {expenses.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    No expenses found.
                  </td>
                </tr>
              ) : (
                expenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(expense.expense_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{expense.employee_name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{expense.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 capitalize">{expense.category}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(expense.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(expense.status)}`}>
                        {expense.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        {expense.status === 'pending' && (
                          <>
                            <button
                              onClick={() => approveExpense(expense.id)}
                              className="text-green-600 hover:text-green-900"
                              title="Approve"
                            >
                              ✓
                            </button>
                            <button
                              onClick={() => rejectExpense(expense.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Reject"
                            >
                              ✕
                            </button>
                          </>
                        )}
                        <button className="text-blue-600 hover:text-blue-900" title="View Details">👁️</button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
