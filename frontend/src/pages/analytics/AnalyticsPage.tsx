import { Card, Button, Badge } from '@components/common'
import { FiTrendingUp, FiTrendingDown, FiDollarSign, FiUsers, FiDownload } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Business intelligence and insights</p>
        </div>
        <Button leftIcon={<FiDownload />}>Export Report</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiTrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Revenue Growth</p>
              <p className="text-xl font-bold text-green-600">+23.5%</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg. Deal Size</p>
              <p className="text-xl font-bold">{formatCurrency(42500000)}</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <FiUsers className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">New Customers</p>
              <p className="text-xl font-bold">156</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiTrendingDown className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Churn Rate</p>
              <p className="text-xl font-bold text-yellow-600">-2.3%</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Revenue by Department" padding="md">
          <div className="space-y-3">
            {[
              { name: 'Sales', revenue: 850000000, percentage: 35 },
              { name: 'Services', revenue: 680000000, percentage: 28 },
              { name: 'Consulting', revenue: 510000000, percentage: 21 },
              { name: 'Support', revenue: 390000000, percentage: 16 },
            ].map((dept, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{dept.name}</span>
                  <span className="text-sm font-bold text-gray-900">{formatCurrency(dept.revenue)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${dept.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Top Performing Products" padding="md">
          <div className="space-y-3">
            {[
              { product: 'ERP Enterprise License', sales: 45, revenue: 675000000 },
              { product: 'CRM Pro Subscription', sales: 123, revenue: 492000000 },
              { product: 'Analytics Platform', sales: 78, revenue: 390000000 },
              { product: 'Support Premium Package', sales: 56, revenue: 168000000 },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{item.product}</p>
                  <p className="text-sm text-gray-500">{item.sales} units sold</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-gray-900">{formatCurrency(item.revenue)}</p>
                  <Badge variant="success" size="sm">+{15 + i * 3}%</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card title="Monthly Trends" padding="md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { month: 'October 2025', revenue: 2450000000, growth: 18.5, color: 'green' },
            { month: 'November 2025', revenue: 2680000000, growth: 23.2, color: 'green' },
            { month: 'December 2025', revenue: 2890000000, growth: 27.8, color: 'green' },
          ].map((month, i) => (
            <div key={i} className="p-4 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg">
              <p className="text-sm font-medium text-primary-900">{month.month}</p>
              <p className="text-2xl font-bold text-primary-900 mt-2">{formatCurrency(month.revenue)}</p>
              <div className="flex items-center gap-1 mt-2">
                <FiTrendingUp className={`w-4 h-4 text-${month.color}-600`} />
                <span className={`text-sm font-medium text-${month.color}-600`}>+{month.growth}%</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
