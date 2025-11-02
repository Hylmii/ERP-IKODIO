import { Card, Button, Badge } from '@components/common'
import { FiPlus, FiFileText } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function InvoicesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-600 mt-1">Manage invoices and billing</p>
        </div>
        <Button leftIcon={<FiPlus />}>New Invoice</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiFileText className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Invoices</p>
              <p className="text-xl font-bold">156</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiFileText className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-xl font-bold">23</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiFileText className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Paid</p>
              <p className="text-xl font-bold">120</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiFileText className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Overdue</p>
              <p className="text-xl font-bold">13</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Recent Invoices" padding="md">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[1, 2, 3, 4, 5].map((i) => (
                <tr key={i}>
                  <td className="px-6 py-4 font-medium">INV-202510{i}</td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium">Acme Corporation</p>
                      <p className="text-sm text-gray-500">contact@acme.com</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">Oct {20 + i}, 2025</td>
                  <td className="px-6 py-4 font-semibold">{formatCurrency(15000000 * i)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={i % 3 === 0 ? 'success' : i % 2 === 0 ? 'warning' : 'danger'}>
                      {i % 3 === 0 ? 'Paid' : i % 2 === 0 ? 'Pending' : 'Overdue'}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <Button size="sm" variant="ghost">View</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
