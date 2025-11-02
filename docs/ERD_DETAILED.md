# iKodio ERP - Detailed Entity Relationship Diagram

**Generated:** 2025-11-02 20:44:31

---

## Table of Contents

- [AUTHENTICATION Module](#authentication-module)
- [HR Module](#hr-module)
- [PROJECT Module](#project-module)
- [FINANCE Module](#finance-module)
- [CRM Module](#crm-module)
- [ASSET Module](#asset-module)
- [HELPDESK Module](#helpdesk-module)
- [DMS Module](#dms-module)
- [ANALYTICS Module](#analytics-module)

---

## AUTHENTICATION Module

**Total Models:** 6


### User
**Table:** `users`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `password`: CharField
- `is_superuser`: BooleanField
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `email`: CharField (UNIQUE)
- `username`: CharField (UNIQUE) (NULL)
- `first_name`: CharField
- `last_name`: CharField
- `phone`: CharField
- `avatar`: FileField (NULL)
- `is_active`: BooleanField
- `is_staff`: BooleanField
- `is_verified`: BooleanField
- `department`: CharField
- `position`: CharField
- `employee_id`: CharField (UNIQUE) (NULL)
- `date_joined`: DateTimeField
- `last_login`: DateTimeField (NULL)
- `email_verified_at`: DateTimeField (NULL)
- `role`: ForeignKey → authentication.Role (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- role → authentication.Role

**Many-to-Many:**
- groups ↔ auth.Group
- user_permissions ↔ auth.Permission


### Role
**Table:** `roles`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `code`: CharField (UNIQUE)
- `description`: TextField
- `is_system_role`: BooleanField
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User

**Many-to-Many:**
- permissions ↔ authentication.Permission


### Permission
**Table:** `permissions`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `resource`: CharField
- `action`: CharField
- `code`: CharField (UNIQUE)
- `description`: TextField
- `is_active`: BooleanField


### UserSession
**Table:** `user_sessions`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `user`: ForeignKey → authentication.User
- `token`: CharField (UNIQUE)
- `ip_address`: GenericIPAddressField
- `user_agent`: CharField
- `device_type`: CharField
- `location`: CharField
- `is_active`: BooleanField
- `expires_at`: DateTimeField
- `last_activity`: DateTimeField

**Foreign Keys:**
- user → authentication.User


### AuditLog
**Table:** `audit_logs`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `user`: ForeignKey → authentication.User (NULL)
- `action`: CharField
- `resource_type`: CharField
- `resource_id`: CharField
- `description`: TextField
- `ip_address`: GenericIPAddressField (NULL)
- `user_agent`: CharField
- `changes`: JSONField (NULL)
- `metadata`: JSONField (NULL)

**Foreign Keys:**
- user → authentication.User


### PasswordResetToken
**Table:** `password_reset_tokens`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `user`: ForeignKey → authentication.User
- `token`: CharField (UNIQUE)
- `expires_at`: DateTimeField
- `is_used`: BooleanField
- `used_at`: DateTimeField (NULL)
- `ip_address`: GenericIPAddressField (NULL)

**Foreign Keys:**
- user → authentication.User

## HR Module

**Total Models:** 8


### Employee
**Table:** `employees`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `user`: OneToOneField → authentication.User (UNIQUE)
- `employee_id`: CharField (UNIQUE)
- `first_name`: CharField
- `last_name`: CharField
- `email`: CharField (UNIQUE)
- `phone`: CharField
- `mobile`: CharField
- `date_of_birth`: DateField
- `gender`: CharField
- `marital_status`: CharField
- `nationality`: CharField
- `id_card_number`: CharField (UNIQUE)
- `tax_id`: CharField (UNIQUE)
- `passport_number`: CharField
- `address`: TextField
- `city`: CharField
- `province`: CharField
- `postal_code`: CharField
- `employment_type`: CharField
- `employment_status`: CharField
- `join_date`: DateField
- `probation_end_date`: DateField (NULL)
- `contract_end_date`: DateField (NULL)
- `resign_date`: DateField (NULL)
- `department`: ForeignKey → hr.Department
- `position`: ForeignKey → hr.Position
- `reporting_to`: ForeignKey → hr.Employee (NULL)
- `base_salary`: DecimalField
- `bank_name`: CharField
- `bank_account_number`: CharField
- `bank_account_holder`: CharField
- `emergency_contact_name`: CharField
- `emergency_contact_relationship`: CharField
- `emergency_contact_phone`: CharField
- `photo`: FileField (NULL)
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- user → authentication.User
- department → hr.Department
- position → hr.Position
- reporting_to → hr.Employee


### Department
**Table:** `departments`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `code`: CharField (UNIQUE)
- `description`: TextField
- `parent`: ForeignKey → hr.Department (NULL)
- `head`: ForeignKey → hr.Employee (NULL)
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- parent → hr.Department
- head → hr.Employee


### Position
**Table:** `positions`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `title`: CharField
- `code`: CharField (UNIQUE)
- `description`: TextField
- `level`: CharField
- `department`: ForeignKey → hr.Department
- `min_salary`: DecimalField
- `max_salary`: DecimalField
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- department → hr.Department


### Attendance
**Table:** `attendances`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `employee`: ForeignKey → hr.Employee
- `date`: DateField
- `status`: CharField
- `clock_in`: TimeField (NULL)
- `clock_out`: TimeField (NULL)
- `clock_in_location`: CharField
- `clock_out_location`: CharField
- `working_hours`: DecimalField
- `overtime_hours`: DecimalField
- `is_approved`: BooleanField
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)
- `notes`: TextField

**Foreign Keys:**
- employee → hr.Employee
- approved_by → hr.Employee


### Leave
**Table:** `leaves`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `employee`: ForeignKey → hr.Employee
- `leave_type`: CharField
- `start_date`: DateField
- `end_date`: DateField
- `total_days`: IntegerField
- `reason`: TextField
- `attachment`: FileField (NULL)
- `status`: CharField
- `reviewed_by`: ForeignKey → hr.Employee (NULL)
- `reviewed_at`: DateTimeField (NULL)
- `review_notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee
- reviewed_by → hr.Employee


### LeaveBalance
**Table:** `leave_balances`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `employee`: ForeignKey → hr.Employee
- `year`: IntegerField
- `annual_quota`: IntegerField
- `annual_used`: IntegerField
- `sick_quota`: IntegerField
- `sick_used`: IntegerField
- `compensatory_quota`: IntegerField
- `compensatory_used`: IntegerField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee


### Payroll
**Table:** `payrolls`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `employee`: ForeignKey → hr.Employee
- `period_month`: IntegerField
- `period_year`: IntegerField
- `basic_salary`: DecimalField
- `allowances`: DecimalField
- `overtime_pay`: DecimalField
- `bonus`: DecimalField
- `tax`: DecimalField
- `insurance`: DecimalField
- `pension`: DecimalField
- `loan_deduction`: DecimalField
- `other_deductions`: DecimalField
- `gross_salary`: DecimalField
- `total_deductions`: DecimalField
- `net_salary`: DecimalField
- `working_days`: IntegerField
- `present_days`: IntegerField
- `overtime_hours`: DecimalField
- `status`: CharField
- `calculated_at`: DateTimeField (NULL)
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)
- `paid_at`: DateTimeField (NULL)
- `payslip_file`: FileField (NULL)
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee
- approved_by → hr.Employee


### PerformanceReview
**Table:** `performance_reviews`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `employee`: ForeignKey → hr.Employee
- `reviewer`: ForeignKey → hr.Employee (NULL)
- `review_type`: CharField
- `review_period_start`: DateField
- `review_period_end`: DateField
- `review_date`: DateField
- `technical_skills`: IntegerField
- `communication`: IntegerField
- `teamwork`: IntegerField
- `leadership`: IntegerField
- `productivity`: IntegerField
- `quality_of_work`: IntegerField
- `attendance`: IntegerField
- `overall_rating`: DecimalField
- `strengths`: TextField
- `areas_for_improvement`: TextField
- `goals`: TextField
- `reviewer_comments`: TextField
- `employee_comments`: TextField
- `status`: CharField
- `submitted_at`: DateTimeField (NULL)
- `completed_at`: DateTimeField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee
- reviewer → hr.Employee

## PROJECT Module

**Total Models:** 8


### Project
**Table:** `projects`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `code`: CharField (UNIQUE)
- `name`: CharField
- `description`: TextField
- `status`: CharField
- `priority`: CharField
- `client`: ForeignKey → crm.Client
- `start_date`: DateField
- `end_date`: DateField
- `actual_start_date`: DateField (NULL)
- `actual_end_date`: DateField (NULL)
- `estimated_budget`: DecimalField
- `actual_cost`: DecimalField
- `contract_value`: DecimalField
- `currency`: CharField
- `progress_percentage`: DecimalField
- `project_manager`: ForeignKey → hr.Employee
- `contract_document`: FileField (NULL)
- `tags`: CharField
- `category`: CharField
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- project_manager → hr.Employee

**Many-to-Many:**
- team_members ↔ hr.Employee


### ProjectTeamMember
**Table:** `project_team_members`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `project`: ForeignKey → project.Project
- `employee`: ForeignKey → hr.Employee
- `role`: CharField
- `allocation_percentage`: IntegerField
- `start_date`: DateField
- `end_date`: DateField (NULL)
- `is_active`: BooleanField

**Foreign Keys:**
- project → project.Project
- employee → hr.Employee


### Task
**Table:** `tasks`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `task_number`: CharField (UNIQUE)
- `title`: CharField
- `description`: TextField
- `project`: ForeignKey → project.Project
- `sprint`: ForeignKey → project.Sprint (NULL)
- `parent_task`: ForeignKey → project.Task (NULL)
- `assigned_to`: ForeignKey → hr.Employee (NULL)
- `status`: CharField
- `priority`: CharField
- `start_date`: DateField (NULL)
- `due_date`: DateField (NULL)
- `completed_date`: DateField (NULL)
- `estimated_hours`: DecimalField
- `actual_hours`: DecimalField
- `progress_percentage`: DecimalField
- `story_points`: IntegerField (NULL)
- `tags`: CharField
- `attachments`: JSONField (NULL)
- `display_order`: IntegerField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- project → project.Project
- sprint → project.Sprint
- parent_task → project.Task
- assigned_to → hr.Employee


### Sprint
**Table:** `sprints`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `project`: ForeignKey → project.Project
- `name`: CharField
- `goal`: TextField
- `start_date`: DateField
- `end_date`: DateField
- `status`: CharField
- `planned_story_points`: IntegerField
- `completed_story_points`: IntegerField
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- project → project.Project


### Timesheet
**Table:** `timesheets`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `employee`: ForeignKey → hr.Employee
- `task`: ForeignKey → project.Task
- `project`: ForeignKey → project.Project
- `date`: DateField
- `hours`: DecimalField
- `description`: TextField
- `is_billable`: BooleanField
- `hourly_rate`: DecimalField (NULL)
- `is_approved`: BooleanField
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee
- task → project.Task
- project → project.Project
- approved_by → hr.Employee


### ProjectMilestone
**Table:** `project_milestones`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `project`: ForeignKey → project.Project
- `name`: CharField
- `description`: TextField
- `due_date`: DateField
- `completed_date`: DateField (NULL)
- `status`: CharField
- `deliverables`: TextField
- `payment_percentage`: DecimalField
- `display_order`: IntegerField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- project → project.Project


### TaskComment
**Table:** `task_comments`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `task`: ForeignKey → project.Task
- `author`: ForeignKey → hr.Employee
- `comment`: TextField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- task → project.Task
- author → hr.Employee


### ProjectRisk
**Table:** `project_risks`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `project`: ForeignKey → project.Project
- `title`: CharField
- `description`: TextField
- `severity`: CharField
- `probability`: IntegerField
- `impact`: IntegerField
- `mitigation_plan`: TextField
- `contingency_plan`: TextField
- `status`: CharField
- `owner`: ForeignKey → hr.Employee (NULL)
- `identified_date`: DateField
- `resolved_date`: DateField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- project → project.Project
- owner → hr.Employee

## FINANCE Module

**Total Models:** 10


### GeneralLedger
**Table:** `general_ledger`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `code`: CharField (UNIQUE)
- `name`: CharField
- `description`: TextField
- `account_type`: CharField
- `parent`: ForeignKey → finance.GeneralLedger (NULL)
- `is_active`: BooleanField
- `is_header`: BooleanField
- `currency`: CharField
- `balance`: DecimalField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- parent → finance.GeneralLedger


### JournalEntry
**Table:** `journal_entries`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `entry_number`: CharField (UNIQUE)
- `entry_date`: DateField
- `description`: TextField
- `reference_number`: CharField
- `status`: CharField
- `posted_by`: ForeignKey → hr.Employee (NULL)
- `posted_at`: DateTimeField (NULL)
- `reversed_entry`: ForeignKey → finance.JournalEntry (NULL)
- `reversed_at`: DateTimeField (NULL)
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- posted_by → hr.Employee
- reversed_entry → finance.JournalEntry


### JournalEntryLine
**Table:** `journal_entry_lines`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `journal_entry`: ForeignKey → finance.JournalEntry
- `account`: ForeignKey → finance.GeneralLedger
- `description`: CharField
- `debit`: DecimalField
- `credit`: DecimalField
- `project`: ForeignKey → project.Project (NULL)
- `department`: ForeignKey → hr.Department (NULL)

**Foreign Keys:**
- journal_entry → finance.JournalEntry
- account → finance.GeneralLedger
- project → project.Project
- department → hr.Department


### Invoice
**Table:** `invoices`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `invoice_number`: CharField (UNIQUE)
- `invoice_type`: CharField
- `invoice_date`: DateField
- `due_date`: DateField
- `client`: ForeignKey → crm.Client
- `project`: ForeignKey → project.Project (NULL)
- `subtotal`: DecimalField
- `tax_amount`: DecimalField
- `discount_amount`: DecimalField
- `total_amount`: DecimalField
- `paid_amount`: DecimalField
- `outstanding_amount`: DecimalField
- `currency`: CharField
- `tax_percentage`: DecimalField
- `tax_number`: CharField
- `status`: CharField
- `payment_terms`: TextField
- `notes`: TextField
- `internal_notes`: TextField
- `invoice_file`: FileField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- project → project.Project


### InvoiceLine
**Table:** `invoice_lines`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `invoice`: ForeignKey → finance.Invoice
- `description`: CharField
- `quantity`: DecimalField
- `unit_price`: DecimalField
- `discount_percentage`: DecimalField
- `tax_percentage`: DecimalField
- `amount`: DecimalField
- `account`: ForeignKey → finance.GeneralLedger (NULL)
- `line_number`: IntegerField

**Foreign Keys:**
- invoice → finance.Invoice
- account → finance.GeneralLedger


### Payment
**Table:** `payments`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `payment_number`: CharField (UNIQUE)
- `payment_type`: CharField
- `payment_date`: DateField
- `client`: ForeignKey → crm.Client (NULL)
- `invoice`: ForeignKey → finance.Invoice (NULL)
- `amount`: DecimalField
- `currency`: CharField
- `payment_method`: CharField
- `reference_number`: CharField
- `bank_name`: CharField
- `bank_account`: CharField
- `status`: CharField
- `account`: ForeignKey → finance.GeneralLedger
- `notes`: TextField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- invoice → finance.Invoice
- account → finance.GeneralLedger


### Expense
**Table:** `expenses`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `expense_number`: CharField (UNIQUE)
- `expense_date`: DateField
- `employee`: ForeignKey → hr.Employee
- `category`: CharField
- `description`: TextField
- `amount`: DecimalField
- `currency`: CharField
- `project`: ForeignKey → project.Project (NULL)
- `department`: ForeignKey → hr.Department (NULL)
- `account`: ForeignKey → finance.GeneralLedger
- `status`: CharField
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)
- `approval_notes`: TextField
- `paid_at`: DateTimeField (NULL)
- `payment_reference`: CharField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- employee → hr.Employee
- project → project.Project
- department → hr.Department
- account → finance.GeneralLedger
- approved_by → hr.Employee


### Budget
**Table:** `budgets`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField
- `description`: TextField
- `fiscal_year`: IntegerField
- `start_date`: DateField
- `end_date`: DateField
- `department`: ForeignKey → hr.Department (NULL)
- `project`: ForeignKey → project.Project (NULL)
- `total_budget`: DecimalField
- `total_spent`: DecimalField
- `total_committed`: DecimalField
- `currency`: CharField
- `status`: CharField
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- department → hr.Department
- project → project.Project
- approved_by → hr.Employee


### BudgetLine
**Table:** `budget_lines`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `budget`: ForeignKey → finance.Budget
- `account`: ForeignKey → finance.GeneralLedger
- `allocated_amount`: DecimalField
- `spent_amount`: DecimalField
- `committed_amount`: DecimalField
- `notes`: TextField

**Foreign Keys:**
- budget → finance.Budget
- account → finance.GeneralLedger


### Tax
**Table:** `taxes`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `tax_number`: CharField (UNIQUE)
- `tax_type`: CharField
- `tax_period_month`: IntegerField
- `tax_period_year`: IntegerField
- `taxable_amount`: DecimalField
- `tax_rate`: DecimalField
- `tax_amount`: DecimalField
- `status`: CharField
- `filing_date`: DateField (NULL)
- `payment_date`: DateField (NULL)
- `reference_number`: CharField
- `tax_report`: FileField (NULL)
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User

## CRM Module

**Total Models:** 7


### Client
**Table:** `clients`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `code`: CharField (UNIQUE)
- `name`: CharField
- `client_type`: CharField
- `email`: CharField
- `phone`: CharField
- `mobile`: CharField
- `website`: CharField
- `address`: TextField
- `city`: CharField
- `province`: CharField
- `postal_code`: CharField
- `country`: CharField
- `tax_id`: CharField
- `company_registration`: CharField
- `industry`: CharField
- `contact_person_name`: CharField
- `contact_person_title`: CharField
- `contact_person_email`: CharField
- `contact_person_phone`: CharField
- `status`: CharField
- `account_manager`: ForeignKey → hr.Employee (NULL)
- `credit_limit`: DecimalField
- `payment_terms_days`: IntegerField
- `rating`: IntegerField (NULL)
- `notes`: TextField
- `tags`: CharField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- account_manager → hr.Employee


### Lead
**Table:** `leads`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `lead_number`: CharField (UNIQUE)
- `company_name`: CharField
- `contact_name`: CharField
- `title`: CharField
- `email`: CharField
- `phone`: CharField
- `mobile`: CharField
- `city`: CharField
- `province`: CharField
- `country`: CharField
- `source`: CharField
- `industry`: CharField
- `estimated_value`: DecimalField (NULL)
- `assigned_to`: ForeignKey → hr.Employee (NULL)
- `status`: CharField
- `is_qualified`: BooleanField
- `qualified_at`: DateTimeField (NULL)
- `converted_opportunity`: ForeignKey → crm.Opportunity (NULL)
- `converted_at`: DateTimeField (NULL)
- `description`: TextField
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- assigned_to → hr.Employee
- converted_opportunity → crm.Opportunity


### Opportunity
**Table:** `opportunities`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `opportunity_number`: CharField (UNIQUE)
- `name`: CharField
- `description`: TextField
- `client`: ForeignKey → crm.Client (NULL)
- `lead`: ForeignKey → crm.Lead (NULL)
- `stage`: CharField
- `probability`: IntegerField
- `estimated_value`: DecimalField
- `expected_revenue`: DecimalField
- `currency`: CharField
- `expected_close_date`: DateField
- `actual_close_date`: DateField (NULL)
- `owner`: ForeignKey → hr.Employee
- `competitors`: TextField
- `is_won`: BooleanField
- `win_loss_reason`: TextField
- `project`: ForeignKey → project.Project (NULL)
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- lead → crm.Lead
- owner → hr.Employee
- project → project.Project


### Contract
**Table:** `contracts`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `contract_number`: CharField (UNIQUE)
- `contract_type`: CharField
- `title`: CharField
- `description`: TextField
- `client`: ForeignKey → crm.Client
- `opportunity`: ForeignKey → crm.Opportunity (NULL)
- `project`: ForeignKey → project.Project (NULL)
- `start_date`: DateField
- `end_date`: DateField
- `signed_date`: DateField (NULL)
- `contract_value`: DecimalField
- `currency`: CharField
- `status`: CharField
- `is_auto_renewable`: BooleanField
- `renewal_notice_days`: IntegerField
- `payment_terms`: TextField
- `terms_and_conditions`: TextField
- `owner`: ForeignKey → hr.Employee
- `contract_file`: FileField (NULL)
- `signed_contract_file`: FileField (NULL)
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- opportunity → crm.Opportunity
- project → project.Project
- owner → hr.Employee


### Quotation
**Table:** `quotations`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `quotation_number`: CharField (UNIQUE)
- `title`: CharField
- `description`: TextField
- `client`: ForeignKey → crm.Client
- `opportunity`: ForeignKey → crm.Opportunity (NULL)
- `quotation_date`: DateField
- `valid_until`: DateField
- `subtotal`: DecimalField
- `discount_amount`: DecimalField
- `tax_amount`: DecimalField
- `total_amount`: DecimalField
- `currency`: CharField
- `tax_percentage`: DecimalField
- `status`: CharField
- `prepared_by`: ForeignKey → hr.Employee
- `accepted_at`: DateTimeField (NULL)
- `rejected_at`: DateTimeField (NULL)
- `rejection_reason`: TextField
- `payment_terms`: TextField
- `notes`: TextField
- `terms_and_conditions`: TextField
- `quotation_file`: FileField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- client → crm.Client
- opportunity → crm.Opportunity
- prepared_by → hr.Employee


### QuotationLine
**Table:** `quotation_lines`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `quotation`: ForeignKey → crm.Quotation
- `description`: CharField
- `quantity`: DecimalField
- `unit_price`: DecimalField
- `discount_percentage`: DecimalField
- `amount`: DecimalField
- `line_number`: IntegerField
- `notes`: TextField

**Foreign Keys:**
- quotation → crm.Quotation


### FollowUp
**Table:** `follow_ups`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `lead`: ForeignKey → crm.Lead (NULL)
- `opportunity`: ForeignKey → crm.Opportunity (NULL)
- `client`: ForeignKey → crm.Client (NULL)
- `activity_type`: CharField
- `subject`: CharField
- `description`: TextField
- `scheduled_date`: DateTimeField
- `completed_date`: DateTimeField (NULL)
- `assigned_to`: ForeignKey → hr.Employee
- `status`: CharField
- `outcome`: TextField
- `next_action`: TextField
- `send_reminder`: BooleanField
- `reminder_sent`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- lead → crm.Lead
- opportunity → crm.Opportunity
- client → crm.Client
- assigned_to → hr.Employee

## ASSET Module

**Total Models:** 8


### Asset
**Table:** `assets`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `asset_number`: CharField (UNIQUE)
- `name`: CharField
- `description`: TextField
- `asset_type`: CharField
- `category`: ForeignKey → asset.AssetCategory
- `manufacturer`: CharField
- `model_number`: CharField
- `serial_number`: CharField (UNIQUE) (NULL)
- `vendor`: ForeignKey → asset.Vendor (NULL)
- `purchase_date`: DateField (NULL)
- `purchase_cost`: DecimalField (NULL)
- `currency`: CharField
- `warranty_start`: DateField (NULL)
- `warranty_end`: DateField (NULL)
- `warranty_provider`: CharField
- `license_key`: CharField
- `license_start`: DateField (NULL)
- `license_end`: DateField (NULL)
- `license_seats`: IntegerField (NULL)
- `license_used_seats`: IntegerField
- `assigned_to`: ForeignKey → hr.Employee (NULL)
- `assigned_date`: DateField (NULL)
- `location`: CharField
- `status`: CharField
- `depreciation_method`: CharField
- `useful_life_years`: IntegerField (NULL)
- `salvage_value`: DecimalField
- `current_value`: DecimalField (NULL)
- `image`: FileField (NULL)
- `documents`: JSONField (NULL)
- `notes`: TextField
- `tags`: CharField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- category → asset.AssetCategory
- vendor → asset.Vendor
- assigned_to → hr.Employee


### AssetCategory
**Table:** `asset_categories`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `code`: CharField (UNIQUE)
- `description`: TextField
- `parent`: ForeignKey → asset.AssetCategory (NULL)
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- parent → asset.AssetCategory


### Vendor
**Table:** `vendors`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `code`: CharField (UNIQUE)
- `name`: CharField
- `email`: CharField
- `phone`: CharField
- `website`: CharField
- `address`: TextField
- `city`: CharField
- `province`: CharField
- `postal_code`: CharField
- `country`: CharField
- `tax_id`: CharField
- `contact_person_name`: CharField
- `contact_person_phone`: CharField
- `contact_person_email`: CharField
- `status`: CharField
- `rating`: IntegerField (NULL)
- `payment_terms_days`: IntegerField
- `notes`: TextField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User


### Procurement
**Table:** `procurements`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `procurement_number`: CharField (UNIQUE)
- `title`: CharField
- `description`: TextField
- `requested_by`: ForeignKey → hr.Employee
- `department`: ForeignKey → hr.Department
- `vendor`: ForeignKey → asset.Vendor (NULL)
- `priority`: CharField
- `status`: CharField
- `request_date`: DateField
- `required_date`: DateField
- `ordered_date`: DateField (NULL)
- `received_date`: DateField (NULL)
- `total_amount`: DecimalField
- `currency`: CharField
- `budget`: ForeignKey → finance.Budget (NULL)
- `approved_by`: ForeignKey → hr.Employee (NULL)
- `approved_at`: DateTimeField (NULL)
- `approval_notes`: TextField
- `po_number`: CharField
- `notes`: TextField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- requested_by → hr.Employee
- department → hr.Department
- vendor → asset.Vendor
- budget → finance.Budget
- approved_by → hr.Employee


### ProcurementLine
**Table:** `procurement_lines`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `procurement`: ForeignKey → asset.Procurement
- `description`: CharField
- `quantity`: DecimalField
- `unit_price`: DecimalField
- `amount`: DecimalField
- `asset_category`: ForeignKey → asset.AssetCategory (NULL)
- `quantity_received`: DecimalField
- `line_number`: IntegerField
- `notes`: TextField

**Foreign Keys:**
- procurement → asset.Procurement
- asset_category → asset.AssetCategory


### AssetMaintenance
**Table:** `asset_maintenances`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `asset`: ForeignKey → asset.Asset
- `maintenance_number`: CharField (UNIQUE)
- `maintenance_type`: CharField
- `title`: CharField
- `description`: TextField
- `scheduled_date`: DateField
- `start_date`: DateField (NULL)
- `completion_date`: DateField (NULL)
- `assigned_to`: ForeignKey → hr.Employee (NULL)
- `vendor`: ForeignKey → asset.Vendor (NULL)
- `status`: CharField
- `estimated_cost`: DecimalField (NULL)
- `actual_cost`: DecimalField (NULL)
- `currency`: CharField
- `work_performed`: TextField
- `parts_replaced`: TextField
- `next_maintenance_date`: DateField (NULL)
- `notes`: TextField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- asset → asset.Asset
- assigned_to → hr.Employee
- vendor → asset.Vendor


### AssetAssignment
**Table:** `asset_assignments`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `asset`: ForeignKey → asset.Asset
- `employee`: ForeignKey → hr.Employee
- `assigned_date`: DateField
- `returned_date`: DateField (NULL)
- `location`: CharField
- `condition_at_assignment`: TextField
- `condition_at_return`: TextField
- `is_active`: BooleanField
- `notes`: TextField

**Foreign Keys:**
- asset → asset.Asset
- employee → hr.Employee


### License
**Table:** `licenses`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `license_number`: CharField (UNIQUE)
- `software_name`: CharField
- `version`: CharField
- `publisher`: CharField
- `license_type`: CharField
- `license_key`: CharField
- `total_seats`: IntegerField
- `used_seats`: IntegerField
- `purchase_date`: DateField
- `start_date`: DateField
- `end_date`: DateField (NULL)
- `status`: CharField
- `purchase_cost`: DecimalField
- `annual_cost`: DecimalField (NULL)
- `currency`: CharField
- `vendor`: ForeignKey → asset.Vendor (NULL)
- `is_auto_renewable`: BooleanField
- `renewal_notice_days`: IntegerField
- `owner`: ForeignKey → hr.Employee (NULL)
- `notes`: TextField
- `documents`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- vendor → asset.Vendor
- owner → hr.Employee

## HELPDESK Module

**Total Models:** 6


### Ticket
**Table:** `tickets`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `ticket_number`: CharField (UNIQUE)
- `subject`: CharField
- `description`: TextField
- `category`: CharField
- `priority`: CharField
- `requester`: ForeignKey → hr.Employee
- `requester_email`: CharField
- `requester_phone`: CharField
- `client`: ForeignKey → crm.Client (NULL)
- `assigned_to`: ForeignKey → hr.Employee (NULL)
- `assigned_team`: ForeignKey → hr.Department (NULL)
- `status`: CharField
- `sla_policy`: ForeignKey → helpdesk.SLAPolicy (NULL)
- `due_date`: DateTimeField (NULL)
- `response_due`: DateTimeField (NULL)
- `resolution_due`: DateTimeField (NULL)
- `first_response_at`: DateTimeField (NULL)
- `resolved_at`: DateTimeField (NULL)
- `closed_at`: DateTimeField (NULL)
- `resolution`: TextField
- `resolution_time_hours`: DecimalField (NULL)
- `related_project`: ForeignKey → project.Project (NULL)
- `related_asset`: ForeignKey → asset.Asset (NULL)
- `satisfaction_rating`: IntegerField (NULL)
- `satisfaction_feedback`: TextField
- `tags`: CharField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- requester → hr.Employee
- client → crm.Client
- assigned_to → hr.Employee
- assigned_team → hr.Department
- sla_policy → helpdesk.SLAPolicy
- related_project → project.Project
- related_asset → asset.Asset


### TicketComment
**Table:** `ticket_comments`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `ticket`: ForeignKey → helpdesk.Ticket
- `author`: ForeignKey → hr.Employee
- `comment`: TextField
- `is_internal`: BooleanField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- ticket → helpdesk.Ticket
- author → hr.Employee


### SLAPolicy
**Table:** `sla_policies`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `description`: TextField
- `priority`: CharField
- `response_time_hours`: IntegerField
- `resolution_time_hours`: IntegerField
- `is_business_hours_only`: BooleanField
- `business_hours_start`: TimeField
- `business_hours_end`: TimeField
- `include_weekends`: BooleanField
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User


### TicketEscalation
**Table:** `ticket_escalations`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `ticket`: ForeignKey → helpdesk.Ticket
- `escalated_from`: ForeignKey → hr.Employee (NULL)
- `escalated_to`: ForeignKey → hr.Employee (NULL)
- `reason`: TextField
- `escalation_level`: IntegerField
- `resolved`: BooleanField
- `resolved_at`: DateTimeField (NULL)

**Foreign Keys:**
- ticket → helpdesk.Ticket
- escalated_from → hr.Employee
- escalated_to → hr.Employee


### KnowledgeBase
**Table:** `knowledge_base`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `article_number`: CharField (UNIQUE)
- `title`: CharField
- `content`: TextField
- `summary`: TextField
- `category`: CharField
- `author`: ForeignKey → hr.Employee
- `status`: CharField
- `published_at`: DateTimeField (NULL)
- `view_count`: IntegerField
- `helpful_count`: IntegerField
- `not_helpful_count`: IntegerField
- `keywords`: CharField
- `tags`: CharField
- `attachments`: JSONField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- author → hr.Employee


### TicketTemplate
**Table:** `ticket_templates`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `description`: TextField
- `subject_template`: CharField
- `description_template`: TextField
- `default_category`: CharField
- `default_priority`: CharField
- `default_assigned_team`: ForeignKey → hr.Department (NULL)
- `sla_policy`: ForeignKey → helpdesk.SLAPolicy (NULL)
- `is_active`: BooleanField
- `usage_count`: IntegerField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- default_assigned_team → hr.Department
- sla_policy → helpdesk.SLAPolicy

## DMS Module

**Total Models:** 7


### Document
**Table:** `documents`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `document_number`: CharField (UNIQUE)
- `title`: CharField
- `description`: TextField
- `document_type`: CharField
- `file`: FileField
- `file_name`: CharField
- `file_size`: BigIntegerField
- `file_extension`: CharField
- `mime_type`: CharField
- `version`: CharField
- `is_latest_version`: BooleanField
- `parent_document`: ForeignKey → dms.Document (NULL)
- `category`: ForeignKey → dms.DocumentCategory (NULL)
- `tags`: CharField
- `keywords`: CharField
- `owner`: ForeignKey → hr.Employee
- `status`: CharField
- `expiry_date`: DateField (NULL)
- `is_expired`: BooleanField
- `is_public`: BooleanField
- `is_confidential`: BooleanField
- `department`: ForeignKey → hr.Department (NULL)
- `project`: ForeignKey → project.Project (NULL)
- `client`: ForeignKey → crm.Client (NULL)
- `download_count`: IntegerField
- `view_count`: IntegerField
- `checksum`: CharField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- parent_document → dms.Document
- category → dms.DocumentCategory
- owner → hr.Employee
- department → hr.Department
- project → project.Project
- client → crm.Client


### DocumentCategory
**Table:** `document_categories`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `code`: CharField (UNIQUE)
- `description`: TextField
- `parent`: ForeignKey → dms.DocumentCategory (NULL)
- `is_restricted`: BooleanField
- `icon`: CharField
- `color`: CharField
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- parent → dms.DocumentCategory


### DocumentVersion
**Table:** `document_versions`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `document`: ForeignKey → dms.Document
- `version_number`: CharField
- `file`: FileField
- `file_size`: BigIntegerField
- `checksum`: CharField
- `change_summary`: TextField
- `uploaded_by`: ForeignKey → hr.Employee

**Foreign Keys:**
- document → dms.Document
- uploaded_by → hr.Employee


### DocumentApproval
**Table:** `document_approvals`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `document`: ForeignKey → dms.Document
- `approver`: ForeignKey → hr.Employee
- `status`: CharField
- `approval_level`: IntegerField
- `due_date`: DateField (NULL)
- `approved_at`: DateTimeField (NULL)
- `comments`: TextField
- `signature`: FileField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- document → dms.Document
- approver → hr.Employee


### DocumentAccess
**Table:** `document_accesses`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `document`: ForeignKey → dms.Document
- `employee`: ForeignKey → hr.Employee (NULL)
- `department`: ForeignKey → hr.Department (NULL)
- `role`: ForeignKey → authentication.Role (NULL)
- `can_view`: BooleanField
- `can_download`: BooleanField
- `can_edit`: BooleanField
- `can_delete`: BooleanField
- `can_share`: BooleanField
- `expires_at`: DateTimeField (NULL)
- `granted_by`: ForeignKey → hr.Employee

**Foreign Keys:**
- document → dms.Document
- employee → hr.Employee
- department → hr.Department
- role → authentication.Role
- granted_by → hr.Employee


### DocumentTemplate
**Table:** `document_templates`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField (UNIQUE)
- `description`: TextField
- `template_type`: CharField
- `file`: FileField
- `file_extension`: CharField
- `variables`: JSONField (NULL)
- `category`: ForeignKey → dms.DocumentCategory (NULL)
- `usage_count`: IntegerField
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- category → dms.DocumentCategory


### DocumentActivity
**Table:** `document_activities`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `document`: ForeignKey → dms.Document
- `user`: ForeignKey → hr.Employee (NULL)
- `activity_type`: CharField
- `description`: TextField
- `ip_address`: GenericIPAddressField (NULL)
- `user_agent`: CharField
- `metadata`: JSONField (NULL)

**Foreign Keys:**
- document → dms.Document
- user → hr.Employee

## ANALYTICS Module

**Total Models:** 8


### Dashboard
**Table:** `dashboards`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField
- `description`: TextField
- `dashboard_type`: CharField
- `owner`: ForeignKey → hr.Employee
- `is_public`: BooleanField
- `layout_config`: JSONField (NULL)
- `auto_refresh`: BooleanField
- `refresh_interval_minutes`: IntegerField
- `display_order`: IntegerField
- `is_active`: BooleanField
- `is_default`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- owner → hr.Employee

**Many-to-Many:**
- shared_with_departments ↔ hr.Department
- shared_with_employees ↔ hr.Employee


### Widget
**Table:** `widgets`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `dashboard`: ForeignKey → analytics.Dashboard
- `title`: CharField
- `description`: TextField
- `widget_type`: CharField
- `data_source`: CharField
- `query_config`: JSONField (NULL)
- `display_config`: JSONField (NULL)
- `position_x`: IntegerField
- `position_y`: IntegerField
- `width`: IntegerField
- `height`: IntegerField
- `auto_refresh`: BooleanField
- `refresh_interval_minutes`: IntegerField
- `display_order`: IntegerField
- `is_visible`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- dashboard → analytics.Dashboard


### Report
**Table:** `reports`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField
- `description`: TextField
- `report_type`: CharField
- `owner`: ForeignKey → hr.Employee
- `data_source`: CharField
- `query_config`: JSONField (NULL)
- `template_config`: JSONField (NULL)
- `columns_config`: JSONField (NULL)
- `filters_config`: JSONField (NULL)
- `grouping_config`: JSONField (NULL)
- `sorting_config`: JSONField (NULL)
- `default_format`: CharField
- `is_scheduled`: BooleanField
- `schedule_cron`: CharField
- `email_recipients`: JSONField (NULL)
- `is_public`: BooleanField
- `run_count`: IntegerField
- `last_run_at`: DateTimeField (NULL)
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- owner → hr.Employee


### ReportExecution
**Table:** `report_executions`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `report`: ForeignKey → analytics.Report
- `executed_by`: ForeignKey → hr.Employee (NULL)
- `parameters`: JSONField (NULL)
- `status`: CharField
- `started_at`: DateTimeField
- `completed_at`: DateTimeField (NULL)
- `duration_seconds`: IntegerField (NULL)
- `output_format`: CharField
- `output_file`: FileField (NULL)
- `output_size_bytes`: BigIntegerField (NULL)
- `row_count`: IntegerField (NULL)
- `error_message`: TextField

**Foreign Keys:**
- report → analytics.Report
- executed_by → hr.Employee


### KPI
**Table:** `kpis`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField
- `description`: TextField
- `kpi_type`: CharField
- `owner`: ForeignKey → hr.Employee
- `department`: ForeignKey → hr.Department (NULL)
- `project`: ForeignKey → project.Project (NULL)
- `calculation_method`: TextField
- `data_source`: CharField
- `query_config`: JSONField (NULL)
- `target_value`: DecimalField
- `current_value`: DecimalField
- `threshold_red`: DecimalField (NULL)
- `threshold_yellow`: DecimalField (NULL)
- `threshold_green`: DecimalField (NULL)
- `unit`: CharField
- `frequency`: CharField
- `period_start`: DateField (NULL)
- `period_end`: DateField (NULL)
- `last_calculated_at`: DateTimeField (NULL)
- `is_active`: BooleanField

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- owner → hr.Employee
- department → hr.Department
- project → project.Project


### KPIValue
**Table:** `kpi_values`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `kpi`: ForeignKey → analytics.KPI
- `period_date`: DateField
- `value`: DecimalField
- `target_value`: DecimalField
- `variance`: DecimalField
- `variance_percentage`: DecimalField
- `status`: CharField
- `notes`: TextField

**Foreign Keys:**
- kpi → analytics.KPI


### DataExport
**Table:** `data_exports`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `export_type`: CharField
- `export_format`: CharField
- `requested_by`: ForeignKey → hr.Employee (NULL)
- `filters`: JSONField (NULL)
- `status`: CharField
- `output_file`: FileField (NULL)
- `file_size_bytes`: BigIntegerField (NULL)
- `row_count`: IntegerField (NULL)
- `started_at`: DateTimeField
- `completed_at`: DateTimeField (NULL)
- `expires_at`: DateTimeField (NULL)
- `error_message`: TextField

**Foreign Keys:**
- requested_by → hr.Employee


### SavedFilter
**Table:** `saved_filters`

**Fields:**
- `id`: BigAutoField (PK) (UNIQUE)
- `created_at`: DateTimeField
- `updated_at`: DateTimeField
- `is_deleted`: BooleanField
- `deleted_at`: DateTimeField (NULL)
- `deleted_by`: ForeignKey → authentication.User (NULL)
- `created_by`: ForeignKey → authentication.User (NULL)
- `updated_by`: ForeignKey → authentication.User (NULL)
- `name`: CharField
- `description`: TextField
- `filter_type`: CharField
- `owner`: ForeignKey → hr.Employee
- `filter_config`: JSONField
- `is_public`: BooleanField
- `usage_count`: IntegerField
- `last_used_at`: DateTimeField (NULL)

**Foreign Keys:**
- deleted_by → authentication.User
- created_by → authentication.User
- updated_by → authentication.User
- owner → hr.Employee


---

## Summary

- **Total Modules:** 9
- **Total Models:** 68
- **Database:** PostgreSQL 15+
- **ORM:** Django ORM
