import { Card, Button, Badge } from '@components/common'
import { FiPlus, FiHeadphones, FiClock, FiCheckCircle } from 'react-icons/fi'

export default function HelpdeskPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Helpdesk</h1>
          <p className="text-gray-600 mt-1">Manage support tickets and requests</p>
        </div>
        <Button leftIcon={<FiPlus />}>New Ticket</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiHeadphones className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Tickets</p>
              <p className="text-xl font-bold">156</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiHeadphones className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Open</p>
              <p className="text-xl font-bold">34</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiClock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-xl font-bold">18</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiCheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Resolved</p>
              <p className="text-xl font-bold">104</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Recent Tickets" padding="md">
        <div className="space-y-3">
          {[
            { id: 'TKT-001', title: 'Cannot login to system', priority: 'high', status: 'open' },
            { id: 'TKT-002', title: 'Printer not working', priority: 'medium', status: 'in_progress' },
            { id: 'TKT-003', title: 'Request new software license', priority: 'low', status: 'pending' },
            { id: 'TKT-004', title: 'Email not receiving', priority: 'high', status: 'open' },
            { id: 'TKT-005', title: 'VPN connection issue', priority: 'medium', status: 'resolved' },
          ].map((ticket, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-sm">{ticket.id}</span>
                  <Badge variant={
                    ticket.priority === 'high' ? 'danger' :
                    ticket.priority === 'medium' ? 'warning' : 'default'
                  } size="sm">
                    {ticket.priority}
                  </Badge>
                </div>
                <p className="text-gray-900 mt-1">{ticket.title}</p>
                <p className="text-sm text-gray-500 mt-1">Created 2 hours ago</p>
              </div>
              <Badge variant={
                ticket.status === 'open' ? 'danger' :
                ticket.status === 'in_progress' ? 'warning' :
                ticket.status === 'resolved' ? 'success' : 'default'
              }>
                {ticket.status.replace('_', ' ')}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
