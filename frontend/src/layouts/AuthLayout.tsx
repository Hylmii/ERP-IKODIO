import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Ikodio ERP</h1>
            <p className="text-gray-600 mt-2">Enterprise Resource Planning System</p>
          </div>
          
          <Outlet />
        </div>
        
        <div className="text-center mt-6 text-white text-sm">
          <p>&copy; {new Date().getFullYear()} Ikodio. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
