import { useState } from 'react'
import { Card, Button, Badge } from '@components/common'
import { FiPlus } from 'react-icons/fi'

export default function TasksPage() {
  const [activeTab, setActiveTab] = useState('kanban')

  const columns = ['To Do', 'In Progress', 'Review', 'Done']

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-600 mt-1">Manage tasks with Kanban board</p>
        </div>
        <Button leftIcon={<FiPlus />}>New Task</Button>
      </div>

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('kanban')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'kanban'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600'
          }`}
        >
          Kanban Board
        </button>
        <button
          onClick={() => setActiveTab('list')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'list'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600'
          }`}
        >
          List View
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {columns.map((column) => (
          <Card key={column} title={column} padding="sm">
            <div className="space-y-3">
              {[1, 2, 3].map((task) => (
                <div
                  key={task}
                  className="p-3 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                >
                  <h4 className="font-medium text-sm mb-2">
                    Implement user authentication
                  </h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Add JWT authentication with refresh tokens
                  </p>
                  <div className="flex items-center justify-between">
                    <Badge variant="primary" size="sm">
                      High
                    </Badge>
                    <div className="flex items-center gap-1">
                      <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center text-xs font-medium text-primary-700">
                        JD
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
