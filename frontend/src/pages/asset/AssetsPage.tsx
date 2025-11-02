import { Card, Button, Badge } from '@components/common'
import { FiPlus, FiPackage, FiTool, FiAlertCircle } from 'react-icons/fi'
import { formatCurrency } from '@utils/helpers'

export default function AssetsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IT Assets</h1>
          <p className="text-gray-600 mt-1">Manage IT assets and inventory</p>
        </div>
        <Button leftIcon={<FiPlus />}>Add Asset</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiPackage className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Assets</p>
              <p className="text-xl font-bold">256</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiPackage className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">In Use</p>
              <p className="text-xl font-bold">198</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiTool className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Maintenance Due</p>
              <p className="text-xl font-bold">8</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiAlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Broken/Retired</p>
              <p className="text-xl font-bold">12</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Asset Inventory" padding="md">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned To</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[
                { id: 'AST-001', name: 'MacBook Pro 16"', category: 'Laptop', user: 'John Doe', value: 35000000, status: 'in_use' },
                { id: 'AST-002', name: 'Dell Monitor 27"', category: 'Monitor', user: 'Jane Smith', value: 8000000, status: 'in_use' },
                { id: 'AST-003', name: 'HP Printer LaserJet', category: 'Printer', user: 'Office', value: 12000000, status: 'available' },
                { id: 'AST-004', name: 'iPhone 15 Pro', category: 'Mobile', user: 'Bob Wilson', value: 18000000, status: 'in_use' },
                { id: 'AST-005', name: 'Surface Pro 9', category: 'Tablet', user: null, value: 22000000, status: 'maintenance' },
              ].map((asset, i) => (
                <tr key={i}>
                  <td className="px-6 py-4 font-medium">{asset.id}</td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium">{asset.name}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">{asset.category}</td>
                  <td className="px-6 py-4 text-sm">{asset.user || '-'}</td>
                  <td className="px-6 py-4 text-sm">{formatCurrency(asset.value)}</td>
                  <td className="px-6 py-4">
                    <Badge variant={
                      asset.status === 'in_use' ? 'success' :
                      asset.status === 'available' ? 'primary' :
                      asset.status === 'maintenance' ? 'warning' : 'danger'
                    }>
                      {asset.status.replace('_', ' ')}
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
