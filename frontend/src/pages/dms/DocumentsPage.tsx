import { Card, Button, Badge } from '@components/common'
import { FiPlus, FiFile, FiCheckCircle, FiClock, FiAlertCircle } from 'react-icons/fi'
import { formatDate } from '@utils/helpers'

export default function DocumentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Manage and share documents</p>
        </div>
        <Button leftIcon={<FiPlus />}>Upload Document</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiFile className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Documents</p>
              <p className="text-xl font-bold">342</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiCheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-xl font-bold">298</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiClock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pending Review</p>
              <p className="text-xl font-bold">32</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiAlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Expired</p>
              <p className="text-xl font-bold">12</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Recent Documents" padding="md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { name: 'Employee Handbook 2025', category: 'Policy', version: 'v2.1', status: 'approved' },
            { name: 'Project Proposal - ERP System', category: 'Proposal', version: 'v1.3', status: 'pending' },
            { name: 'Q4 Financial Report', category: 'Finance', version: 'v1.0', status: 'approved' },
            { name: 'Data Privacy Policy', category: 'Policy', version: 'v3.0', status: 'approved' },
            { name: 'Meeting Minutes - Jan 2025', category: 'Minutes', version: 'v1.0', status: 'pending' },
            { name: 'Software License Agreement', category: 'Legal', version: 'v2.0', status: 'approved' },
          ].map((doc, i) => (
            <Card key={i} padding="md" className="hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-primary-50 rounded">
                  <FiFile className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate">{doc.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{doc.category}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-gray-400">{doc.version}</span>
                    <Badge variant={doc.status === 'approved' ? 'success' : 'warning'} size="sm">
                      {doc.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">{formatDate(new Date(2025, 0, i + 1))}</p>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100">
                <Button size="sm" variant="ghost" className="w-full">View Document</Button>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  )
}
