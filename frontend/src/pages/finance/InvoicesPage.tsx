import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import financeService from '@/services/financeService'
import type { Invoice, InvoiceFilters } from '@/types/finance'

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [filters, setFilters] = useState<InvoiceFilters>({
    search: '',
    status: undefined,
    invoice_type: undefined,
    date_from: undefined,
    date_to: undefined,
  })
  
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const pageSize = 20

  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    sent: 0,
    paid: 0,
    overdue: 0,
    total_revenue: 0,
    outstanding: 0,
  })

  useEffect(() => {
    fetchInvoices()
  }, [currentPage, filters])

  const fetchInvoices = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await financeService.getInvoices({
        ...filters,
        page: currentPage,
        page_size: pageSize,
      })
      
      setInvoices(response.results)
      setTotalCount(response.count)
      setTotalPages(Math.ceil(response.count / pageSize))
      
      const allInvoices = response.results
      setStats({
        total: allInvoices.length,
        draft: allInvoices.filter(inv => inv.status === 'draft').length,
        sent: allInvoices.filter(inv => inv.status === 'sent').length,
        paid: allInvoices.filter(inv => inv.status === 'paid').length,
        overdue: allInvoices.filter(inv => inv.status === 'overdue').length,
        total_revenue: allInvoices
          .filter(inv => inv.status === 'paid')
          .reduce((sum, inv) => sum + Number(inv.total_amount), 0),
        outstanding: allInvoices
          .filter(inv => ['sent', 'overdue', 'partial'].includes(inv.status))
          .reduce((sum, inv) => sum + Number(inv.total_amount) - Number(inv.paid_amount || 0), 0),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch invoices')
      console.error('Error fetching invoices:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: keyof InvoiceFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }))
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setFilters({
      search: '',
      status: undefined,
      invoice_type: undefined,
      date_from: undefined,
      date_to: undefined,
    })
    setCurrentPage(1)
  }

  const downloadPDF = async (invoiceId: string, invoiceNumber: string) => {
    try {
      const blob = await financeService.downloadInvoicePDF(invoiceId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Invoice-${invoiceNumber}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      alert('Failed to download PDF: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const sendInvoice = async (id: string) => {
    if (!confirm('Send this invoice to client?')) return
    try {
      await financeService.sendInvoice(id)
      alert('Invoice sent successfully!')
      fetchInvoices()
    } catch (err) {
      alert('Failed to send invoice: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const markPaid = async (id: string) => {
    const paymentDate = prompt('Enter payment date (YYYY-MM-DD):')
    if (!paymentDate) return
    
    const paymentMethod = prompt('Payment method (cash/bank_transfer/credit_card/check):')
    if (!paymentMethod) return
    
    try {
      await financeService.markInvoicePaid(id, {
        payment_date: paymentDate,
        payment_method: paymentMethod,
        notes: 'Manual payment confirmation',
      })
      alert('Invoice marked as paid!')
      fetchInvoices()
    } catch (err) {
      alert('Failed to mark as paid: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const cancelInvoice = async (id: string) => {
    const reason = prompt('Reason for cancellation:')
    if (!reason) return
    
    if (!confirm('Are you sure you want to cancel this invoice?')) return
    try {
      await financeService.cancelInvoice(id, reason)
      alert('Invoice cancelled!')
      fetchInvoices()
    } catch (err) {
      alert('Failed to cancel invoice: ' + (err instanceof Error ? err.message : 'Unknown error'))
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      sent: 'bg-blue-100 text-blue-800',
      paid: 'bg-green-100 text-green-800',
      partial: 'bg-yellow-100 text-yellow-800',
      overdue: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-600',
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

  if (loading && invoices.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading invoices...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-sm text-gray-500 mt-1">Manage sales and purchase invoices</p>
        </div>
        <Link
          to="/finance/invoices/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Create Invoice
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Invoices</div>
          <div className="text-2xl font-bold text-gray-900">{totalCount}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Total Revenue (Paid)</div>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(stats.total_revenue)}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Outstanding</div>
          <div className="text-2xl font-bold text-orange-600">
            {formatCurrency(stats.outstanding)}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-sm text-gray-500 mb-1">Overdue</div>
          <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="Search invoice number, client..."
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <select
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="partial">Partial</option>
            <option value="overdue">Overdue</option>
            <option value="cancelled">Cancelled</option>
          </select>

          <select
            value={filters.invoice_type || ''}
            onChange={(e) => handleFilterChange('invoice_type', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="sales">Sales Invoice</option>
            <option value="purchase">Purchase Invoice</option>
          </select>

          <input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => handleFilterChange('date_from', e.target.value)}
            placeholder="From Date"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => handleFilterChange('date_to', e.target.value)}
            placeholder="To Date"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        {(filters.search || filters.status || filters.invoice_type || filters.date_from || filters.date_to) && (
          <button
            onClick={clearFilters}
            className="mt-3 text-sm text-blue-600 hover:text-blue-800"
          >
            Clear all filters
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    No invoices found. Create your first invoice!
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/finance/invoices/${invoice.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-800"
                      >
                        {invoice.invoice_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{invoice.client_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 capitalize">{invoice.invoice_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(invoice.invoice_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(invoice.due_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(invoice.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(invoice.status)}`}>
                        {invoice.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => downloadPDF(invoice.id, invoice.invoice_number)} className="text-gray-600 hover:text-gray-900" title="Download PDF">📄</button>
                        {invoice.status === 'draft' && (
                          <button onClick={() => sendInvoice(invoice.id)} className="text-blue-600 hover:text-blue-900" title="Send Invoice">📧</button>
                        )}
                        {['sent', 'overdue', 'partial'].includes(invoice.status) && (
                          <button onClick={() => markPaid(invoice.id)} className="text-green-600 hover:text-green-900" title="Mark as Paid">✓</button>
                        )}
                        {invoice.status !== 'cancelled' && invoice.status !== 'paid' && (
                          <button onClick={() => cancelInvoice(invoice.id)} className="text-red-600 hover:text-red-900" title="Cancel Invoice">✕</button>
                        )}
                        <Link to={`/finance/invoices/${invoice.id}`} className="text-blue-600 hover:text-blue-900" title="View Details">👁️</Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing page <span className="font-medium">{currentPage}</span> of{' '}
                  <span className="font-medium">{totalPages}</span> ({totalCount} total invoices)
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => i + 1).map(page => (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        currentPage === page
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
