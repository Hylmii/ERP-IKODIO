import api from './api'
import { Employee, Attendance, Payroll, Leave } from '@/types/hr'
import { PaginatedResponse, PaginationParams } from '@/types/common'

export const hrService = {
  // Employees
  getEmployees: async (params?: PaginationParams): Promise<PaginatedResponse<Employee>> => {
    const response = await api.get('/hr/employees/', { params })
    return response.data
  },

  getEmployee: async (id: string): Promise<Employee> => {
    const response = await api.get(`/hr/employees/${id}/`)
    return response.data
  },

  createEmployee: async (data: Partial<Employee>): Promise<Employee> => {
    const response = await api.post('/hr/employees/', data)
    return response.data
  },

  updateEmployee: async (id: string, data: Partial<Employee>): Promise<Employee> => {
    const response = await api.patch(`/hr/employees/${id}/`, data)
    return response.data
  },

  deleteEmployee: async (id: string): Promise<void> => {
    await api.delete(`/hr/employees/${id}/`)
  },

  // Attendance
  getAttendance: async (params?: PaginationParams): Promise<PaginatedResponse<Attendance>> => {
    const response = await api.get('/hr/attendance/', { params })
    return response.data
  },

  clockIn: async (data: { location?: string; device_type: string }): Promise<Attendance> => {
    const response = await api.post('/hr/attendance/clock-in/', data)
    return response.data
  },

  clockOut: async (id: string): Promise<Attendance> => {
    const response = await api.post(`/hr/attendance/${id}/clock-out/`)
    return response.data
  },

  // Payroll
  getPayrolls: async (params?: PaginationParams): Promise<PaginatedResponse<Payroll>> => {
    const response = await api.get('/hr/payroll/', { params })
    return response.data
  },

  generatePayroll: async (data: {
    period_start: string
    period_end: string
    employee_ids?: string[]
  }): Promise<Payroll[]> => {
    const response = await api.post('/hr/payroll/generate/', data)
    return response.data
  },

  approvePayroll: async (id: string): Promise<Payroll> => {
    const response = await api.post(`/hr/payroll/${id}/approve/`)
    return response.data
  },

  // Leave Management
  getLeaves: async (params?: PaginationParams): Promise<PaginatedResponse<Leave>> => {
    const response = await api.get('/hr/leave/', { params })
    return response.data
  },

  requestLeave: async (data: Partial<Leave>): Promise<Leave> => {
    const response = await api.post('/hr/leave/', data)
    return response.data
  },

  approveLeave: async (id: string): Promise<Leave> => {
    const response = await api.post(`/hr/leave/${id}/approve/`)
    return response.data
  },

  rejectLeave: async (id: string, reason: string): Promise<Leave> => {
    const response = await api.post(`/hr/leave/${id}/reject/`, { reason })
    return response.data
  },
}
