import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'
import {
  FiHome,
  FiUsers,
  FiBriefcase,
  FiDollarSign,
  FiPackage,
  FiHeadphones,
  FiFileText,
  FiBarChart2,
  FiMenu,
  FiX,
  FiLogOut,
  FiUser,
  FiSettings,
} from 'react-icons/fi'
import { HiUserGroup } from 'react-icons/hi'
import { getInitials } from '@utils/helpers'

interface NavItem {
  name: string
  path: string
  icon: React.ReactNode
  children?: NavItem[]
}

const navigation: NavItem[] = [
  { name: 'Dashboard', path: '/', icon: <FiHome /> },
  {
    name: 'HR & Talent',
    path: '/hr',
    icon: <FiUsers />,
    children: [
      { name: 'Employees', path: '/hr/employees', icon: <HiUserGroup /> },
      { name: 'Attendance', path: '/hr/attendance', icon: <FiUsers /> },
      { name: 'Payroll', path: '/hr/payroll', icon: <FiDollarSign /> },
    ],
  },
  { name: 'Projects', path: '/projects', icon: <FiBriefcase /> },
  { name: 'Finance', path: '/finance', icon: <FiDollarSign /> },
  { name: 'CRM', path: '/crm', icon: <HiUserGroup /> },
  { name: 'Assets', path: '/assets', icon: <FiPackage /> },
  { name: 'Helpdesk', path: '/helpdesk', icon: <FiHeadphones /> },
  { name: 'Documents', path: '/documents', icon: <FiFileText /> },
  { name: 'Analytics', path: '/analytics', icon: <FiBarChart2 /> },
]

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, clearAuth } = useAuthStore()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-40 h-screen transition-transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } w-64 bg-white border-r border-gray-200`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <h1 className="text-xl font-bold text-primary-600">Ikodio ERP</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-md hover:bg-gray-100"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 overflow-y-auto custom-scrollbar">
            <ul className="space-y-1">
              {navigation.map((item) => (
                <li key={item.path}>
                  {item.children ? (
                    <div>
                      <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {item.name}
                      </div>
                      <ul className="mt-1 space-y-1">
                        {item.children.map((child) => (
                          <li key={child.path}>
                            <Link
                              to={child.path}
                              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                                isActive(child.path)
                                  ? 'bg-primary-50 text-primary-700'
                                  : 'text-gray-700 hover:bg-gray-100'
                              }`}
                            >
                              <span className="text-lg">{child.icon}</span>
                              <span>{child.name}</span>
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <Link
                      to={item.path}
                      className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        isActive(item.path)
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <span className="text-lg">{item.icon}</span>
                      <span>{item.name}</span>
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`${sidebarOpen ? 'lg:pl-64' : ''} transition-all duration-300`}>
        {/* Top Navigation */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md hover:bg-gray-100"
            >
              <FiMenu className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-4">
              {/* Profile Menu */}
              <div className="relative">
                <button
                  onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100"
                >
                  <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center font-medium text-sm">
                    {user ? getInitials(user.full_name) : 'U'}
                  </div>
                  <div className="text-left hidden md:block">
                    <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                    <p className="text-xs text-gray-500">{user?.role}</p>
                  </div>
                </button>

                {profileMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setProfileMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                      <Link
                        to="/profile"
                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setProfileMenuOpen(false)}
                      >
                        <FiUser className="w-4 h-4" />
                        Profile
                      </Link>
                      <Link
                        to="/settings"
                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setProfileMenuOpen(false)}
                      >
                        <FiSettings className="w-4 h-4" />
                        Settings
                      </Link>
                      <hr className="my-1" />
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <FiLogOut className="w-4 h-4" />
                        Logout
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
