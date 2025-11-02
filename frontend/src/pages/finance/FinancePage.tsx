import { Card, Badge } from '@components/common'
import { FiDollarSign, FiTrendingUp, FiTrendingDown, FiPieChart } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function FinancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Finance Overview</h1>
        <p className="text-gray-600 mt-1">Financial performance and analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiTrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Revenue</p>
              <p className="text-xl font-bold">{formatCurrency(2450000000)}</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiTrendingDown className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Expenses</p>
              <p className="text-xl font-bold">{formatCurrency(1200000000)}</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Net Profit</p>
              <p className="text-xl font-bold text-green-600">{formatCurrency(1250000000)}</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiPieChart className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Budget Used</p>
              <p className="text-xl font-bold">68%</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Recent Transactions" padding="md">
          <div className="space-y-3">
            {[
              { type: 'income', desc: 'Client Payment - Project A', amount: 50000000 },
              { type: 'expense', desc: 'Office Rent', amount: -15000000 },
              { type: 'income', desc: 'Service Fee', amount: 25000000 },
              { type: 'expense', desc: 'Salaries', amount: -450000000 },
              { type: 'income', desc: 'Consulting Fee', amount: 30000000 },
            ].map((tx, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">{tx.desc}</p>
                  <p className="text-xs text-gray-500">Oct {25 - i}, 2025</p>
                </div>
                <p className={`font-semibold ${tx.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                  {tx.type === 'income' ? '+' : ''}{formatCurrency(tx.amount)}
                </p>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Budget Overview" padding="md">
          <div className="space-y-4">
            {[
              { category: 'Operations', budget: 500000000, used: 340000000, percentage: 68 },
              { category: 'Marketing', budget: 200000000, used: 150000000, percentage: 75 },
              { category: 'R&D', budget: 300000000, used: 180000000, percentage: 60 },
              { category: 'HR', budget: 600000000, used: 520000000, percentage: 87 },
            ].map((item, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{item.category}</span>
                  <span className="text-sm text-gray-600">
                    {formatCurrency(item.used)} / {formatCurrency(item.budget)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      item.percentage > 80 ? 'bg-red-600' : item.percentage > 60 ? 'bg-yellow-600' : 'bg-green-600'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
