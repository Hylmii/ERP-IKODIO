import { useEffect, useState } from 'react'
import { useAuthStore } from '@store/authStore'
import { Card, Badge, LoadingContent } from '@components/common'
import { 
  FiUsers, 
  FiBriefcase, 
  FiDollarSign, 
  FiPackage,
  FiHeadphones,
  FiFileText,
  FiTrendingUp,
  FiClock,
  FiAlertCircle,
} from 'react-icons/fi'
import { HiUserGroup } from 'react-icons/hi'
import { formatCurrency } from '@utils/helpers'

interface DashboardStats {
  hr: {
    total_employees: number
    present_today: number
    on_leave: number
    pending_payroll: number
  }
  projects: {
    total_projects: number
    active_projects: number
    completed_this_month: number
    total_tasks: number
    overdue_tasks: number
  }
  finance: {
    total_revenue: number
    pending_invoices: number
    pending_expenses: number
    budget_utilization: number
  }
  crm: {
    total_clients: number
    active_leads: number
    opportunities_value: number
    won_this_month: number
  }
  assets: {
    total_assets: number
    maintenance_due: number
    pending_procurement: number
  }
  helpdesk: {
    total_tickets: number
    open_tickets: number
    pending_tickets: number
    avg_resolution_time: number
  }
  documents: {
    total_documents: number
    pending_approval: number
    expiring_soon: number
  }
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  onClick?: () => void
}

const colorClasses = {
  primary: 'bg-primary-50 text-primary-600',
  success: 'bg-green-50 text-green-600',
  warning: 'bg-yellow-50 text-yellow-600',
  danger: 'bg-red-50 text-red-600',
  info: 'bg-blue-50 text-blue-600',
}

function StatCard({ title, value, icon, trend, color, onClick }: StatCardProps) {
  return (
    <Card 
      padding="md" 
      hoverable 
      onClick={onClick}
      className="cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <div className="flex items-center gap-1 mt-2">
              <FiTrendingUp 
                className={`w-4 h-4 ${trend.isPositive ? 'text-green-600' : 'text-red-600 rotate-180'}`}
              />
              <span className={`text-sm font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trend.value}%
              </span>
              <span className="text-sm text-gray-500">vs last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </Card>
  )
}

export default function DashboardHome() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      // In real app, you'd have a dedicated dashboard endpoint
      // For now, we'll simulate loading
      setTimeout(() => {
        setStats({
          hr: {
            total_employees: 145,
            present_today: 132,
            on_leave: 8,
            pending_payroll: 5,
          },
          projects: {
            total_projects: 28,
            active_projects: 15,
            completed_this_month: 3,
            total_tasks: 342,
            overdue_tasks: 12,
          },
          finance: {
            total_revenue: 2450000000,
            pending_invoices: 23,
            pending_expenses: 15,
            budget_utilization: 68,
          },
          crm: {
            total_clients: 89,
            active_leads: 45,
            opportunities_value: 1200000000,
            won_this_month: 8,
          },
          assets: {
            total_assets: 256,
            maintenance_due: 8,
            pending_procurement: 12,
          },
          helpdesk: {
            total_tickets: 156,
            open_tickets: 34,
            pending_tickets: 18,
            avg_resolution_time: 4.2,
          },
          documents: {
            total_documents: 1024,
            pending_approval: 12,
            expiring_soon: 6,
          },
        })
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingContent message="Loading dashboard..." />
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome back, {user?.first_name}! 👋
        </h1>
        <p className="text-primary-100">
          Here's what's happening with your business today.
        </p>
      </div>

      {/* Quick Stats */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Employees"
            value={stats?.hr.total_employees || 0}
            icon={<FiUsers className="w-6 h-6" />}
            color="primary"
            trend={{ value: 5, isPositive: true }}
          />
          <StatCard
            title="Active Projects"
            value={stats?.projects.active_projects || 0}
            icon={<FiBriefcase className="w-6 h-6" />}
            color="success"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="Revenue (This Month)"
            value={formatCurrency(stats?.finance.total_revenue || 0)}
            icon={<FiDollarSign className="w-6 h-6" />}
            color="info"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            title="Active Clients"
            value={stats?.crm.total_clients || 0}
            icon={<HiUserGroup className="w-6 h-6" />}
            color="warning"
            trend={{ value: 3, isPositive: true }}
          />
        </div>
      </div>

      {/* Alerts & Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Actions */}
        <Card title="Pending Actions" padding="md">
          <div className="space-y-3">
            {stats && stats.helpdesk.open_tickets > 0 && (
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FiAlertCircle className="w-5 h-5 text-red-600" />
                  <div>
                    <p className="font-medium text-gray-900">Open Support Tickets</p>
                    <p className="text-sm text-gray-600">
                      {stats.helpdesk.open_tickets} tickets need attention
                    </p>
                  </div>
                </div>
                <Badge variant="danger">{stats.helpdesk.open_tickets}</Badge>
              </div>
            )}
            
            {stats && stats.projects.overdue_tasks > 0 && (
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FiClock className="w-5 h-5 text-yellow-600" />
                  <div>
                    <p className="font-medium text-gray-900">Overdue Tasks</p>
                    <p className="text-sm text-gray-600">
                      {stats.projects.overdue_tasks} tasks are overdue
                    </p>
                  </div>
                </div>
                <Badge variant="warning">{stats.projects.overdue_tasks}</Badge>
              </div>
            )}

            {stats && stats.documents.pending_approval > 0 && (
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FiFileText className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">Pending Approvals</p>
                    <p className="text-sm text-gray-600">
                      {stats.documents.pending_approval} documents awaiting approval
                    </p>
                  </div>
                </div>
                <Badge variant="info">{stats.documents.pending_approval}</Badge>
              </div>
            )}
          </div>
        </Card>

        {/* Module Quick Access */}
        <Card title="Quick Access" padding="md">
          <div className="grid grid-cols-2 gap-3">
            <QuickAccessButton 
              icon={<FiUsers />} 
              label="HR" 
              href="/hr/employees" 
            />
            <QuickAccessButton 
              icon={<FiBriefcase />} 
              label="Projects" 
              href="/projects" 
            />
            <QuickAccessButton 
              icon={<FiDollarSign />} 
              label="Finance" 
              href="/finance" 
            />
            <QuickAccessButton 
              icon={<HiUserGroup />} 
              label="CRM" 
              href="/crm" 
            />
            <QuickAccessButton 
              icon={<FiPackage />} 
              label="Assets" 
              href="/assets" 
            />
            <QuickAccessButton 
              icon={<FiHeadphones />} 
              label="Helpdesk" 
              href="/helpdesk" 
            />
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card title="Recent Activity" padding="md">
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
              <div className="w-2 h-2 bg-primary-600 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  <span className="font-medium">John Doe</span> completed task{' '}
                  <span className="font-medium">"Update API Documentation"</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

function QuickAccessButton({ icon, label, href }: { icon: React.ReactNode; label: string; href: string }) {
  return (
    <a
      href={href}
      className="flex flex-col items-center justify-center p-4 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all duration-200 group"
    >
      <div className="text-gray-600 group-hover:text-primary-600 mb-2 text-xl">
        {icon}
      </div>
      <span className="text-sm font-medium text-gray-700 group-hover:text-primary-700">
        {label}
      </span>
    </a>
  )
}

