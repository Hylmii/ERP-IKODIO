import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'

// Layouts
import AuthLayout from '@layouts/AuthLayout'
import DashboardLayout from '@layouts/DashboardLayout'

// Auth Pages
import LoginPage from '@pages/auth/LoginPage'

// Dashboard Pages
import DashboardHome from '@pages/dashboard/DashboardHome'

// HR Pages
import EmployeesPage from '@pages/hr/EmployeesPage'
import AttendancePage from '@pages/hr/AttendancePage'
import PayrollPage from '@pages/hr/PayrollPage'

// Project Pages
import ProjectsPage from '@pages/project/ProjectsPage'
import TasksPage from '@pages/project/TasksPage'

// Finance Pages
import FinancePage from '@pages/finance/FinancePage'
import InvoicesPage from '@pages/finance/InvoicesPage'
import ExpensesPage from '@pages/finance/ExpensesPage'
import PaymentsPage from '@pages/finance/PaymentsPage'
import BudgetPage from '@pages/finance/BudgetPage'
import ReportsPage from '@pages/finance/ReportsPage'

// CRM Pages
import CRMPage from '@pages/crm/CRMPage'
import ClientsPage from '@pages/crm/ClientsPage'

// Asset Pages
import AssetsPage from '@pages/asset/AssetsPage'

// Helpdesk Pages
import HelpdeskPage from '@pages/helpdesk/HelpdeskPage'

// DMS Pages
import DocumentsPage from '@pages/dms/DocumentsPage'

// Analytics Pages
import AnalyticsPage from '@pages/analytics/AnalyticsPage'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected Dashboard Routes */}
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<DashboardHome />} />
        
        {/* HR Routes */}
        <Route path="/hr/employees" element={<EmployeesPage />} />
        <Route path="/hr/attendance" element={<AttendancePage />} />
        <Route path="/hr/payroll" element={<PayrollPage />} />
        
        {/* Project Routes */}
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/tasks" element={<TasksPage />} />
        
        {/* Finance Routes */}
        <Route path="/finance" element={<FinancePage />} />
        <Route path="/finance/invoices" element={<InvoicesPage />} />
        <Route path="/finance/expenses" element={<ExpensesPage />} />
        <Route path="/finance/payments" element={<PaymentsPage />} />
        <Route path="/finance/budgets" element={<BudgetPage />} />
        <Route path="/finance/reports" element={<ReportsPage />} />
        
        {/* CRM Routes */}
        <Route path="/crm" element={<CRMPage />} />
        <Route path="/crm/clients" element={<ClientsPage />} />
        
        {/* Asset Routes */}
        <Route path="/assets" element={<AssetsPage />} />
        
        {/* Helpdesk Routes */}
        <Route path="/helpdesk" element={<HelpdeskPage />} />
        
        {/* DMS Routes */}
        <Route path="/documents" element={<DocumentsPage />} />
        
        {/* Analytics Routes */}
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
