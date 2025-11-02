import { Card, Button, Badge } from '@components/common'
import { FiPlus, FiMail, FiPhone } from 'react-icons/fi'

export default function ClientsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-600 mt-1">Manage your client relationships</p>
        </div>
        <Button leftIcon={<FiPlus />}>Add Client</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} padding="md" hoverable>
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center font-bold text-primary-700">
                    AC
                  </div>
                  <div>
                    <h3 className="font-semibold">Acme Corporation</h3>
                    <p className="text-sm text-gray-500">CL-00{i}</p>
                  </div>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <FiMail className="w-4 h-4" />
                  <span>contact@acme.com</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <FiPhone className="w-4 h-4" />
                  <span>+62 812 3456 7890</span>
                </div>
              </div>
              <div className="flex items-center justify-between pt-3 border-t">
                <span className="text-sm text-gray-600">5 Projects</span>
                <span className="text-sm text-gray-600">12 Contracts</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
