import { Card } from '@components/common'
import { FiUsers, FiTrendingUp, FiTarget, FiDollarSign } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function CRMPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">CRM Dashboard</h1>
        <p className="text-gray-600 mt-1">Customer relationship management overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiUsers className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Clients</p>
              <p className="text-xl font-bold">89</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiTrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Leads</p>
              <p className="text-xl font-bold">45</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiTarget className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Opportunities</p>
              <p className="text-xl font-bold">28</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pipeline Value</p>
              <p className="text-xl font-bold">{formatCurrency(1200000000)}</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Sales Pipeline" padding="md">
          <div className="space-y-3">
            {[
              { stage: 'Prospecting', count: 15, value: 200000000 },
              { stage: 'Qualification', count: 12, value: 350000000 },
              { stage: 'Proposal', count: 8, value: 420000000 },
              { stage: 'Negotiation', count: 5, value: 230000000 },
            ].map((item, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{item.stage}</span>
                  <span className="text-sm text-gray-600">{item.count} opportunities</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="w-full bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${(item.count / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold whitespace-nowrap">
                    {formatCurrency(item.value)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Recent Activities" padding="md">
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                <div className="w-2 h-2 bg-primary-600 rounded-full mt-2" />
                <div>
                  <p className="text-sm text-gray-900">
                    <span className="font-medium">John Doe</span> contacted{' '}
                    <span className="font-medium">Acme Corp</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{i} hours ago</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
