import { useState, useEffect, useCallback } from 'react'
import financeService from '@/services/financeService'
import type { Budget } from '@/types/finance'

export default function BudgetPage() {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [fiscalYear, setFiscalYear] = useState(new Date().getFullYear())
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  const [stats, setStats] = useState({
    total_allocated: 0,
    total_spent: 0,
    avg_utilization: 0,
    over_budget_count: 0,
  })

  const fetchBudgets = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await financeService.getBudgets({
        fiscal_year: fiscalYear,
        status: selectedStatus || undefined,
      })
      
      setBudgets(response.results)
      
      const allBudgets = response.results
      const totalAllocated = allBudgets.reduce((sum, b) => sum + Number(b.total_allocated), 0)
      const totalSpent = allBudgets.reduce((sum, b) => sum + Number(b.total_spent), 0)
      
      setStats({
        total_allocated: totalAllocated,
        total_spent: totalSpent,
        avg_utilization: totalAllocated > 0 ? (totalSpent / totalAllocated) * 100 : 0,
        over_budget_count: allBudgets.filter(b => Number(b.utilization_percentage) > 100).length,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch budgets')
      console.error('Error fetching budgets:', err)
    } finally {
      setLoading(false)
    }
  }, [fiscalYear, selectedStatus])

  useEffect(() => {
    fetchBudgets()
  }, [fetchBudgets])

  const getUtilizationColor = (percentage: number) => {
    if (percentage < 70) return 'text-green-600'
    if (percentage < 90) return 'text-yellow-600'
    if (percentage < 100) return 'text-orange-600'
    return 'text-red-600'
  }

  const getUtilizationBg = (percentage: number) => {
    if (percentage < 70) return 'bg-green-500'
    if (percentage < 90) return 'bg-yellow-500'
    if (percentage < 100) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const formatCurrency = (amount: number | string) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(num)
  }

  if (loading && budgets.length === 0) {
    return <div className="flex items-center justify-center h-64"><div className="text-gray-500">Loading budgets...</div></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Budget Management</h1>
          <p className="text-sm text-gray-500 mt-1">Plan and monitor departmental budgets</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + Create Budget
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Allocated</div>
          <div className="text-2xl font-bold text-blue-600">{formatCurrency(stats.total_allocated)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Spent</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(stats.total_spent)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Avg Utilization</div>
          <div className={`text-2xl font-bold ${getUtilizationColor(stats.avg_utilization)}`}>
            {stats.avg_utilization.toFixed(1)}%
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Over Budget</div>
          <div className="text-2xl font-bold text-red-600">{stats.over_budget_count}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={fiscalYear}
            onChange={(e) => setFiscalYear(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {[2023, 2024, 2025, 2026].map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {budgets.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-500">
            No budgets found for {fiscalYear}. Create your first budget!
          </div>
        ) : (
          budgets.map((budget) => (
            <div key={budget.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{budget.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {budget.department_name && `${budget.department_name} • `}
                    {budget.period_start} to {budget.period_end}
                  </p>
                </div>
                <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                  budget.status === 'active' ? 'bg-green-100 text-green-800' :
                  budget.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                  budget.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {budget.status.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <div className="text-xs text-gray-500">Allocated</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatCurrency(budget.total_allocated)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Spent</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatCurrency(budget.total_spent)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Remaining</div>
                  <div className={`text-lg font-semibold ${
                    Number(budget.remaining_budget) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(budget.remaining_budget)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Utilization</div>
                  <div className={`text-lg font-semibold ${getUtilizationColor(Number(budget.utilization_percentage))}`}>
                    {Number(budget.utilization_percentage).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="mb-2">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Budget Progress</span>
                  <span>{Number(budget.utilization_percentage).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUtilizationBg(Number(budget.utilization_percentage))}`}
                    style={{ width: `${Math.min(Number(budget.utilization_percentage), 100)}%` }}
                  />
                </div>
              </div>

              {budget.notes && (
                <div className="mt-3 text-sm text-gray-600">
                  <span className="font-medium">Notes:</span> {budget.notes}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
