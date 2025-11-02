import { useState } from 'react'
import { Card, Button, Badge } from '@components/common'
import { FiClock, FiLogIn, FiLogOut } from 'react-icons/fi'

export default function AttendancePage() {
  const [isClockedIn, setIsClockedIn] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Attendance</h1>
          <p className="text-gray-600 mt-1">Track employee attendance</p>
        </div>
        <Button
          variant={isClockedIn ? 'danger' : 'primary'}
          leftIcon={isClockedIn ? <FiLogOut /> : <FiLogIn />}
          onClick={() => setIsClockedIn(!isClockedIn)}
        >
          {isClockedIn ? 'Clock Out' : 'Clock In'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiClock className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Present Today</p>
              <p className="text-xl font-bold">132</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiClock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Late</p>
              <p className="text-xl font-bold">5</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiClock className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Absent</p>
              <p className="text-xl font-bold">3</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <FiClock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">On Leave</p>
              <p className="text-xl font-bold">8</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Today's Attendance" padding="md">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
                  JD
                </div>
                <div>
                  <p className="font-medium">John Doe</p>
                  <p className="text-sm text-gray-500">EMP-00{i}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-sm text-gray-500">Check In</p>
                  <p className="font-medium">08:00 AM</p>
                </div>
                <Badge variant="success">Present</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
