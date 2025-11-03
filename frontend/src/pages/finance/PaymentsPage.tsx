import { useState, useEffect, useCallback } from 'react'
import financeService from '@/services/financeService'
import type { Payment, PaymentFilters } from '@/types/finance'

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [filters, setFilters] = useState<PaymentFilters>({
    search: '',
    payment_type: undefined,
    payment_method: undefined,
    status: undefined,
    date_from: undefined,
    date_to: undefined,
  })
  
  const [currentPage] = useState(1)
  const pageSize = 20

  const [stats, setStats] = useState({
    total_receipts: 0,
    total_payments_out: 0,
    pending: 0,
    confirmed: 0,
  })

  const fetchPayments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await financeService.getPayments({
        ...filters,
        page: currentPage,
        page_size: pageSize,
      })
      
      setPayments(response.results)
      // setTotalCount(response.count)
      // setTotalPages(Math.ceil(response.count / pageSize))
      
      const allPayments = response.results
      setStats({
        total_receipts: allPayments
          .filter(p => p.payment_type === 'receipt')
          .reduce((sum, p) => sum + Number(p.amount), 0),
        total_payments_out: allPayments
          .filter(p => p.payment_type === 'payment')
          .reduce((sum, p) => sum + Number(p.amount), 0),
        pending: allPayments.filter(p => p.status === 'pending').length,
        confirmed: allPayments.filter(p => p.status === 'confirmed').length,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch payments')
      console.error('Error fetching payments:', err)
    } finally {
      setLoading(false)
    }
  }, [currentPage, filters])

  useEffect(() => {
    fetchPayments()
  }, [fetchPayments])

  const confirmPayment = async (id: string) => {
    if (!confirm('Confirm this payment?')) return
    try {
      await financeService.confirmPayment(id)
      alert('Payment confirmed!')
      fetchPayments()
    } catch (err) {
      alert('Failed to confirm: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
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

  if (loading && payments.length === 0) {
    return <div className="flex items-center justify-center h-64"><div className="text-gray-500">Loading payments...</div></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-sm text-gray-500 mt-1">Manage receipts and payments</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + Record Payment
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Receipts</div>
          <div className="text-2xl font-bold text-green-600">{formatCurrency(stats.total_receipts)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Payments</div>
          <div className="text-2xl font-bold text-red-600">{formatCurrency(stats.total_payments_out)}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Pending</div>
          <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Confirmed</div>
          <div className="text-2xl font-bold text-green-600">{stats.confirmed}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="Search reference number..."
            value={filters.search || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <select
            value={filters.payment_type || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, payment_type: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="receipt">Receipt</option>
            <option value="payment">Payment</option>
          </select>

          <select
            value={filters.payment_method || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, payment_method: e.target.value || undefined }))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Methods</option>
            <option value="cash">Cash</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="credit_card">Credit Card</option>
            <option value="debit_card">Debit Card</option>
            <option value="check">Check</option>
            <option value="e_wallet">E-Wallet</option>
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reference</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {payments.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">No payments found.</td>
                </tr>
              ) : (
                payments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(payment.payment_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{payment.reference_number}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${payment.payment_type === 'receipt' ? 'text-green-600' : 'text-red-600'}`}>
                        {payment.payment_type === 'receipt' ? '↓ Receipt' : '↑ Payment'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 capitalize">{payment.payment_method.replace('_', ' ')}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{payment.notes || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(payment.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(payment.status)}`}>
                        {payment.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        {payment.status === 'pending' && (
                          <button
                            onClick={() => confirmPayment(payment.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Confirm Payment"
                          >
                            ✓
                          </button>
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
