import { AuditFields, User } from './common'

// Employee Types
export interface Employee extends AuditFields {
  id: string
  employee_id: string  // Changed from employee_code to match API
  full_name: string  // Added from API response
  user_email: string  // Added from API response
  department_name: string  // Changed from nested to flat
  position_title: string  // Changed from nested to flat
  employment_type: string
  employment_status: string  // Changed from status to match API
  join_date: string
  photo?: string | null
  // Optional fields from detailed view
  user?: number
  department?: number
  position?: number
  first_name?: string
  last_name?: string
  email?: string
  phone?: string
  mobile?: string
  date_of_birth?: string
  gender?: string
  marital_status?: string
  nationality?: string
  id_card_number?: string
  tax_id?: string
  passport_number?: string
  address?: string
  city?: string
  province?: string
  postal_code?: string
  probation_end_date?: string
  contract_end_date?: string
  resign_date?: string
  base_salary?: number
  bank_name?: string
  bank_account_number?: string
  bank_account_holder?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relationship?: string
  reporting_to?: number
  manager_name?: string | null
  notes?: string
}

export interface Department {
  id: string
  name: string
  code: string
  manager?: User
  description?: string
}

export interface Position {
  id: string
  title: string
  code: string
  level: string
  department: Department
}

export enum EmploymentType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  CONTRACT = 'contract',
  INTERN = 'intern',
}

export enum EmployeeStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ON_LEAVE = 'on_leave',
  TERMINATED = 'terminated',
}

export interface EmergencyContact {
  name: string
  relationship: string
  phone: string
  address: string
}

export interface EmployeeDocument {
  id: string
  document_type: string
  file_url: string
  uploaded_at: string
}

// Attendance Types
export interface Attendance extends AuditFields {
  id: string
  employee: Employee
  date: string
  check_in: string
  check_out?: string
  status: AttendanceStatus
  notes?: string
  location?: string
  device_type: AttendanceDeviceType
}

export enum AttendanceStatus {
  PRESENT = 'present',
  LATE = 'late',
  ABSENT = 'absent',
  HALF_DAY = 'half_day',
  ON_LEAVE = 'on_leave',
}

export enum AttendanceDeviceType {
  MANUAL = 'manual',
  RFID = 'rfid',
  GPS = 'gps',
  BIOMETRIC = 'biometric',
}

// Payroll Types
export interface Payroll extends AuditFields {
  id: string
  employee: Employee
  period_start: string
  period_end: string
  basic_salary: number
  allowances: PayrollAllowance[]
  deductions: PayrollDeduction[]
  gross_salary: number
  net_salary: number
  status: PayrollStatus
  payment_date?: string
}

export interface PayrollAllowance {
  name: string
  amount: number
}

export interface PayrollDeduction {
  name: string
  amount: number
  type: 'tax' | 'bpjs' | 'loan' | 'other'
}

export enum PayrollStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  PAID = 'paid',
  REJECTED = 'rejected',
}

// Leave Types
export interface Leave extends AuditFields {
  id: string
  employee: Employee
  leave_type: LeaveType
  start_date: string
  end_date: string
  total_days: number
  reason: string
  status: LeaveStatus
  approved_by?: User
  approval_date?: string
  rejection_reason?: string
}

export enum LeaveType {
  ANNUAL = 'annual',
  SICK = 'sick',
  MATERNITY = 'maternity',
  PATERNITY = 'paternity',
  UNPAID = 'unpaid',
}

export enum LeaveStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
}

// KPI/OKR Types
export interface KPI extends AuditFields {
  id: string
  employee: Employee
  title: string
  description: string
  target_value: number
  current_value: number
  unit: string
  period_start: string
  period_end: string
  status: KPIStatus
  score?: number
}

export enum KPIStatus {
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  OVERDUE = 'overdue',
}
