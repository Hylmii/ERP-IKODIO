import { useState } from 'react'
import { financeService } from '../../services/financeService'
import type { ProfitLossReport, BalanceSheet, CashFlowStatement } from '../../types/finance'

type ReportType = 'profit_loss' | 'balance_sheet' | 'cash_flow'

export default function ReportsPage() {
  const [reportType, setReportType] = useState<ReportType>('profit_loss')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [loading, setLoading] = useState(false)
  const [profitLoss, setProfitLoss] = useState<ProfitLossReport | null>(null)
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheet | null>(null)
  const [cashFlow, setCashFlow] = useState<CashFlowStatement | null>(null)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(amount)
  }

  const loadReport = async () => {
    if (!dateFrom || !dateTo) {
      alert('Please select date range')
      return
    }
    setLoading(true)
    try {
      if (reportType === 'profit_loss') {
        const data = await financeService.getProfitLossReport({ start_date: dateFrom, end_date: dateTo })
        setProfitLoss(data)
      } else if (reportType === 'balance_sheet') {
        const data = await financeService.getBalanceSheet({ as_of_date: dateTo })
        setBalanceSheet(data)
      } else if (reportType === 'cash_flow') {
        const data = await financeService.getCashFlowStatement({ start_date: dateFrom, end_date: dateTo })
        setCashFlow(data)
      }
    } catch (error) {
      console.error('Error loading report:', error)
      alert('Failed to load report')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Financial Reports</h1>
        <p className="text-gray-600">Generate comprehensive financial statements</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
            <select value={reportType} onChange={(e) => setReportType(e.target.value as ReportType)} className="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option value="profit_loss">Profit & Loss</option>
              <option value="balance_sheet">Balance Sheet</option>
              <option value="cash_flow">Cash Flow</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
          </div>
          <div className="flex items-end">
            <button onClick={loadReport} disabled={loading} className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400">
              {loading ? 'Loading...' : 'Generate'}
            </button>
          </div>
        </div>
      </div>

      {profitLoss && reportType === 'profit_loss' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Profit & Loss Statement</h2>
          <p className="text-sm text-gray-600 mb-4">Period: {profitLoss.period_start} to {profitLoss.period_end}</p>
          <table className="w-full"><tbody>
            <tr className="bg-blue-50"><td className="py-3 font-bold">Revenue</td><td className="py-3 text-right font-bold">{formatCurrency(profitLoss.revenue.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Sales</td><td className="py-2 text-right">{formatCurrency(profitLoss.revenue.sales)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Services</td><td className="py-2 text-right">{formatCurrency(profitLoss.revenue.services)}</td></tr>
            <tr className="border-b"><td className="py-2 pl-8 text-sm">Other</td><td className="py-2 text-right">{formatCurrency(profitLoss.revenue.other)}</td></tr>
            {profitLoss.cost_of_goods_sold > 0 && <><tr><td className="py-2 text-red-600">COGS</td><td className="py-2 text-right text-red-600">{formatCurrency(profitLoss.cost_of_goods_sold)}</td></tr>
            <tr className="bg-green-50 border-b-2"><td className="py-3 font-bold">Gross Profit</td><td className="py-3 text-right font-bold">{formatCurrency(profitLoss.gross_profit)}</td></tr></>}
            <tr className="bg-orange-50"><td className="py-3 font-bold">Operating Expenses</td><td className="py-3 text-right font-bold">{formatCurrency(profitLoss.operating_expenses.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Salaries</td><td className="py-2 text-right">{formatCurrency(profitLoss.operating_expenses.salaries)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Rent</td><td className="py-2 text-right">{formatCurrency(profitLoss.operating_expenses.rent)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Utilities</td><td className="py-2 text-right">{formatCurrency(profitLoss.operating_expenses.utilities)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Marketing</td><td className="py-2 text-right">{formatCurrency(profitLoss.operating_expenses.marketing)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm">Other</td><td className="py-2 text-right">{formatCurrency(profitLoss.operating_expenses.other)}</td></tr>
            <tr className="bg-yellow-50"><td className="py-3 font-bold">Operating Profit</td><td className="py-3 text-right font-bold">{formatCurrency(profitLoss.operating_profit)}</td></tr>
            <tr className="bg-purple-50"><td className="py-3 font-bold">Profit Before Tax</td><td className="py-3 text-right font-bold">{formatCurrency(profitLoss.profit_before_tax)}</td></tr>
            <tr><td className="py-2 text-red-600">Tax</td><td className="py-2 text-right text-red-600">{formatCurrency(profitLoss.tax)}</td></tr>
            <tr className="bg-green-100 border-t-4 border-green-600"><td className="py-4 text-xl font-bold">NET PROFIT</td><td className="py-4 text-right text-xl font-bold text-green-600">{formatCurrency(profitLoss.net_profit)}</td></tr>
          </tbody></table>
          <div className="mt-6 grid grid-cols-3 gap-4 text-center">
            <div className="bg-blue-50 p-4 rounded"><div className="text-sm text-gray-600">Gross Margin</div><div className="text-xl font-bold">{profitLoss.gross_margin.toFixed(1)}%</div></div>
            <div className="bg-yellow-50 p-4 rounded"><div className="text-sm text-gray-600">Operating Margin</div><div className="text-xl font-bold">{profitLoss.operating_margin.toFixed(1)}%</div></div>
            <div className="bg-green-50 p-4 rounded"><div className="text-sm text-gray-600">Net Margin</div><div className="text-xl font-bold">{profitLoss.net_margin.toFixed(1)}%</div></div>
          </div>
        </div>
      )}

      {balanceSheet && reportType === 'balance_sheet' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Balance Sheet</h2>
          <p className="text-sm text-gray-600 mb-4">As of: {balanceSheet.as_of_date}</p>
          <table className="w-full"><tbody>
            <tr className="bg-blue-50"><td colSpan={2} className="py-3 font-bold text-lg">ASSETS</td></tr>
            <tr className="bg-gray-50"><td className="py-2 pl-4 font-semibold">Current Assets</td><td className="py-2 text-right font-semibold">{formatCurrency(balanceSheet.assets.current_assets.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Cash</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.current_assets.cash)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Accounts Receivable</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.current_assets.accounts_receivable)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Inventory</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.current_assets.inventory)}</td></tr>
            <tr className="border-b"><td className="py-2 pl-8 text-sm">Other</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.current_assets.other)}</td></tr>
            <tr className="bg-gray-50"><td className="py-2 pl-4 font-semibold">Fixed Assets</td><td className="py-2 text-right font-semibold">{formatCurrency(balanceSheet.assets.fixed_assets.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Property</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.fixed_assets.property)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Equipment</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.fixed_assets.equipment)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Vehicles</td><td className="py-2 text-right">{formatCurrency(balanceSheet.assets.fixed_assets.vehicles)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm text-red-600">Depreciation</td><td className="py-2 text-right text-red-600">{formatCurrency(balanceSheet.assets.fixed_assets.accumulated_depreciation)}</td></tr>
            <tr className="bg-blue-100 font-bold"><td className="py-3 pl-4">TOTAL ASSETS</td><td className="py-3 text-right">{formatCurrency(balanceSheet.assets.total)}</td></tr>
            <tr className="bg-red-50"><td colSpan={2} className="py-3 font-bold text-lg">LIABILITIES</td></tr>
            <tr className="bg-gray-50"><td className="py-2 pl-4 font-semibold">Current Liabilities</td><td className="py-2 text-right font-semibold">{formatCurrency(balanceSheet.liabilities.current_liabilities.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Accounts Payable</td><td className="py-2 text-right">{formatCurrency(balanceSheet.liabilities.current_liabilities.accounts_payable)}</td></tr>
            <tr className="border-b"><td className="py-2 pl-8 text-sm">Short-term Loans</td><td className="py-2 text-right">{formatCurrency(balanceSheet.liabilities.current_liabilities.short_term_loans)}</td></tr>
            <tr className="bg-gray-50"><td className="py-2 pl-4 font-semibold">Long-term Liabilities</td><td className="py-2 text-right font-semibold">{formatCurrency(balanceSheet.liabilities.long_term_liabilities.total)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm">Long-term Loans</td><td className="py-2 text-right">{formatCurrency(balanceSheet.liabilities.long_term_liabilities.long_term_loans)}</td></tr>
            <tr className="bg-red-100 font-bold"><td className="py-3 pl-4">TOTAL LIABILITIES</td><td className="py-3 text-right">{formatCurrency(balanceSheet.liabilities.total)}</td></tr>
            <tr className="bg-green-50"><td colSpan={2} className="py-3 font-bold text-lg">EQUITY</td></tr>
            <tr><td className="py-2 pl-4">Capital</td><td className="py-2 text-right">{formatCurrency(balanceSheet.equity.capital)}</td></tr>
            <tr><td className="py-2 pl-4">Retained Earnings</td><td className="py-2 text-right">{formatCurrency(balanceSheet.equity.retained_earnings)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-4">Current Year Profit</td><td className="py-2 text-right">{formatCurrency(balanceSheet.equity.current_year_profit)}</td></tr>
            <tr className="bg-green-100 font-bold"><td className="py-3 pl-4">TOTAL EQUITY</td><td className="py-3 text-right">{formatCurrency(balanceSheet.equity.total)}</td></tr>
            <tr className="bg-purple-100 font-bold border-t-4"><td className="py-4 pl-4 text-lg">TOTAL LIABILITIES & EQUITY</td><td className="py-4 text-right text-lg">{formatCurrency(balanceSheet.total_liabilities_equity)}</td></tr>
          </tbody></table>
        </div>
      )}

      {cashFlow && reportType === 'cash_flow' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Cash Flow Statement</h2>
          <p className="text-sm text-gray-600 mb-4">Period: {cashFlow.period_start} to {cashFlow.period_end}</p>
          <table className="w-full"><tbody>
            <tr className="bg-blue-50"><td className="py-3 font-bold">Operating Activities</td><td className="py-3 text-right font-bold">{formatCurrency(cashFlow.operating_activities.total)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Net Profit</td><td className="py-2 text-right">{formatCurrency(cashFlow.operating_activities.net_profit)}</td></tr>
            <tr><td className="py-2 pl-8 text-sm">Depreciation</td><td className="py-2 text-right">{formatCurrency(cashFlow.operating_activities.depreciation)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm">AR Change</td><td className="py-2 text-right">{formatCurrency(cashFlow.operating_activities.accounts_receivable_change)}</td></tr>
            <tr className="bg-yellow-50"><td className="py-3 font-bold">Investing Activities</td><td className="py-3 text-right font-bold">{formatCurrency(cashFlow.investing_activities.total)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm">Equipment</td><td className="py-2 text-right">{formatCurrency(cashFlow.investing_activities.equipment_purchase)}</td></tr>
            <tr className="bg-green-50"><td className="py-3 font-bold">Financing Activities</td><td className="py-3 text-right font-bold">{formatCurrency(cashFlow.financing_activities.total)}</td></tr>
            <tr className="border-b-2"><td className="py-2 pl-8 text-sm">Loans</td><td className="py-2 text-right">{formatCurrency(cashFlow.financing_activities.loan_received)}</td></tr>
            <tr className="bg-purple-50"><td className="py-3 font-bold">Net Cash Change</td><td className="py-3 text-right font-bold">{formatCurrency(cashFlow.net_cash_flow)}</td></tr>
            <tr><td className="py-2">Opening Cash</td><td className="py-2 text-right">{formatCurrency(cashFlow.opening_cash)}</td></tr>
            <tr className="bg-green-100 border-t-4 border-green-600"><td className="py-4 text-xl font-bold">Closing Cash</td><td className="py-4 text-right text-xl font-bold text-green-600">{formatCurrency(cashFlow.closing_cash)}</td></tr>
          </tbody></table>
        </div>
      )}
    </div>
  )
}
