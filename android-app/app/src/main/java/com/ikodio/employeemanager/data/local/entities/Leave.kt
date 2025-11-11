package com.ikodio.employeemanager.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ForeignKey
import androidx.room.ColumnInfo
import androidx.room.Index
import java.util.Date

/**
 * Leave entity representing leave requests in the database
 */
@Entity(
    tableName = "leaves",
    foreignKeys = [
        ForeignKey(
            entity = Employee::class,
            parentColumns = ["id"],
            childColumns = ["employee_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["employee_id"])]
)
data class Leave(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "employee_id")
    val employeeId: Long,
    
    @ColumnInfo(name = "leave_type")
    val leaveType: LeaveType,
    
    @ColumnInfo(name = "start_date")
    val startDate: Date,
    
    @ColumnInfo(name = "end_date")
    val endDate: Date,
    
    @ColumnInfo(name = "reason")
    val reason: String,
    
    @ColumnInfo(name = "status")
    val status: LeaveStatus,
    
    @ColumnInfo(name = "approved_by")
    val approvedBy: String? = null,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    @ColumnInfo(name = "updated_at")
    val updatedAt: Date = Date()
)

/**
 * Leave type enum
 */
enum class LeaveType {
    CUTI,       // Leave
    SAKIT,      // Sick Leave
    IZIN        // Permission
}

/**
 * Leave status enum
 */
enum class LeaveStatus {
    PENDING,
    APPROVED,
    REJECTED
}
