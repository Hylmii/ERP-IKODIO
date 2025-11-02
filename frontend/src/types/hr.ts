import { AuditFields, User } from './common'

// Employee Types
export interface Employee extends AuditFields {
  id: string
  employee_code: string
  user: User
  department: Department
  position: Position
  employment_type: EmploymentType
  join_date: string
  resignation_date?: string
  salary: number
  status: EmployeeStatus
  skills: string[]
  emergency_contact: EmergencyContact
  documents: EmployeeDocument[]
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
