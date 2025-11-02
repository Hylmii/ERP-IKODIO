import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, Button, Input, Table, Badge, Modal, Pagination, LoadingContent } from '@components/common'
import { FiPlus, FiSearch, FiEdit, FiTrash2, FiMail, FiPhone, FiUser } from 'react-icons/fi'
import { hrService } from '@services/hrService'
import { Employee, EmployeeStatus } from '@types/hr'
import { formatDate } from '@utils/helpers'
import toast from 'react-hot-toast'

export default function EmployeesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)
  const pageSize = 10

  const queryClient = useQueryClient()

  // Fetch employees
  const { data, isLoading, error } = useQuery({
    queryKey: ['employees', currentPage, searchTerm],
    queryFn: () => hrService.getEmployees({
      page: currentPage,
      page_size: pageSize,
      search: searchTerm,
    }),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => hrService.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      toast.success('Employee deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete employee')
    },
  })

  const handleEdit = (employee: Employee) => {
    setSelectedEmployee(employee)
    setIsModalOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status: EmployeeStatus) => {
    const statusConfig: Record<EmployeeStatus, { variant: any; label: string }> = {
      [EmployeeStatus.ACTIVE]: { variant: 'success', label: 'Active' },
      [EmployeeStatus.INACTIVE]: { variant: 'default', label: 'Inactive' },
      [EmployeeStatus.ON_LEAVE]: { variant: 'warning', label: 'On Leave' },
      [EmployeeStatus.TERMINATED]: { variant: 'danger', label: 'Terminated' },
    }

    const config = statusConfig[status]
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  const columns = [
    {
      key: 'employee_code',
      header: 'Employee ID',
      render: (item: Employee) => (
        <div className="font-medium text-gray-900">{item.employee_code}</div>
      ),
    },
    {
      key: 'user',
      header: 'Name',
      render: (item: Employee) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold">
            {item.user.first_name[0]}{item.user.last_name[0]}
          </div>
          <div>
            <div className="font-medium text-gray-900">{item.user.full_name}</div>
            <div className="text-sm text-gray-500">{item.user.email}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'department',
      header: 'Department',
      render: (item: Employee) => (
        <div>
          <div className="text-gray-900">{item.department.name}</div>
          <div className="text-sm text-gray-500">{item.position.title}</div>
        </div>
      ),
    },
    {
      key: 'employment_type',
      header: 'Type',
      render: (item: Employee) => (
        <Badge variant="default">{item.employment_type.replace('_', ' ')}</Badge>
      ),
    },
    {
      key: 'join_date',
      header: 'Join Date',
      render: (item: Employee) => formatDate(item.join_date, 'short'),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item: Employee) => getStatusBadge(item.status),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item: Employee) => (
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            leftIcon={<FiEdit />}
            onClick={() => handleEdit(item)}
          />
          <Button
            size="sm"
            variant="ghost"
            leftIcon={<FiTrash2 />}
            onClick={() => handleDelete(item.id)}
          />
        </div>
      ),
    },
  ]

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load employees. Please try again.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-1">Manage your organization's workforce</p>
        </div>
        <Button
          leftIcon={<FiPlus />}
          onClick={() => {
            setSelectedEmployee(null)
            setIsModalOpen(true)
          }}
        >
          Add Employee
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-50 rounded-lg">
              <FiUser className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Employees</p>
              <p className="text-xl font-bold text-gray-900">{data?.count || 0}</p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-50 rounded-lg">
              <FiUser className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-xl font-bold text-gray-900">
                {data?.results.filter((e: Employee) => e.status === EmployeeStatus.ACTIVE).length || 0}
              </p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <FiUser className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">On Leave</p>
              <p className="text-xl font-bold text-gray-900">
                {data?.results.filter((e: Employee) => e.status === EmployeeStatus.ON_LEAVE).length || 0}
              </p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-50 rounded-lg">
              <FiUser className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Inactive</p>
              <p className="text-xl font-bold text-gray-900">
                {data?.results.filter((e: Employee) => e.status === EmployeeStatus.INACTIVE).length || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card padding="md">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search employees by name, email, or employee ID..."
              leftIcon={<FiSearch />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </Card>

      {/* Employee Table */}
      <Card padding="none">
        {isLoading ? (
          <LoadingContent message="Loading employees..." />
        ) : (
          <>
            <Table
              data={data?.results || []}
              columns={columns}
              keyExtractor={(item) => item.id}
            />
            {data && data.count > pageSize && (
              <div className="p-4 border-t border-gray-200">
                <Pagination
                  currentPage={currentPage}
                  totalPages={Math.ceil(data.count / pageSize)}
                  onPageChange={setCurrentPage}
                  pageSize={pageSize}
                  totalItems={data.count}
                />
              </div>
            )}
          </>
        )}
      </Card>

      {/* Employee Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedEmployee ? 'Edit Employee' : 'Add Employee'}
        size="lg"
      >
        <EmployeeForm
          employee={selectedEmployee}
          onClose={() => setIsModalOpen(false)}
          onSuccess={() => {
            setIsModalOpen(false)
            queryClient.invalidateQueries({ queryKey: ['employees'] })
          }}
        />
      </Modal>
    </div>
  )
}

// Employee Form Component
interface EmployeeFormProps {
  employee: Employee | null
  onClose: () => void
  onSuccess: () => void
}

function EmployeeForm({ employee, onClose, onSuccess }: EmployeeFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Form submission logic here
      toast.success(employee ? 'Employee updated successfully' : 'Employee created successfully')
      onSuccess()
    } catch (error) {
      toast.error('Failed to save employee')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="First Name" required />
        <Input label="Last Name" required />
      </div>
      <Input label="Email" type="email" required leftIcon={<FiMail />} />
      <Input label="Phone" type="tel" leftIcon={<FiPhone />} />
      <Input label="Employee Code" required />
      <div className="grid grid-cols-2 gap-4">
        <Input label="Join Date" type="date" required />
        <Input label="Salary" type="number" required />
      </div>

      <div className="flex items-center justify-end gap-3 pt-4">
        <Button type="button" variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {employee ? 'Update' : 'Create'} Employee
        </Button>
      </div>
    </form>
  )
}

