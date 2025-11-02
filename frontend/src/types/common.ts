// Base API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: {
    message: string
    details?: Record<string, string | number | boolean>
  }
  meta?: {
    total_items?: number
    total_pages?: number
    current_page?: number
    page_size?: number
  }
}

// User & Authentication Types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: UserRole
  department?: string
  position?: string
  avatar?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  ADMIN = 'admin',
  HR_MANAGER = 'hr_manager',
  PROJECT_MANAGER = 'project_manager',
  FINANCE_MANAGER = 'finance_manager',
  EMPLOYEE = 'employee',
  CLIENT = 'client',
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

// Common Types
export interface SelectOption {
  value: string | number
  label: string
}

export interface TimeStamp {
  created_at: string
  updated_at: string
}

export interface AuditFields extends TimeStamp {
  created_by?: User
  updated_by?: User
}

// Pagination
export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}
