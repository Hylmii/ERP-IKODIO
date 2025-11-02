import { Card, Button, Badge } from '@components/common'
import { FiDollarSign, FiCheck, FiFileText } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function PayrollPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payroll</h1>
          <p className="text-gray-600 mt-1">Manage employee compensation</p>
        </div>
        <Button leftIcon={<FiDollarSign />}>Generate Payroll</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Payroll</p>
              <p className="text-xl font-bold">{formatCurrency(450000000)}</p>
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
              <p className="text-xl font-bold">5</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiCheck className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-xl font-bold">140</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <FiDollarSign className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Paid</p>
              <p className="text-xl font-bold">135</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Recent Payroll" padding="md">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gross</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[1, 2, 3, 4, 5].map((i) => (
                <tr key={i}>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium">John Doe</p>
                      <p className="text-sm text-gray-500">EMP-00{i}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">Oct 2025</td>
                  <td className="px-6 py-4 text-sm">{formatCurrency(8000000)}</td>
                  <td className="px-6 py-4 font-semibold text-green-600">{formatCurrency(7200000)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={i % 2 === 0 ? 'success' : 'warning'}>
                      {i % 2 === 0 ? 'Approved' : 'Pending'}
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
