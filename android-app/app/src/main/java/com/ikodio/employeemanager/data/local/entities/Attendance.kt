package com.ikodio.employeemanager.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ForeignKey
import androidx.room.ColumnInfo
import androidx.room.Index
import java.util.Date

/**
 * Attendance entity representing attendance records in the database
 */
@Entity(
    tableName = "attendance",
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
data class Attendance(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "employee_id")
    val employeeId: Long,
    
    @ColumnInfo(name = "date")
    val date: Date,
    
    @ColumnInfo(name = "check_in_time")
    val checkInTime: Date?,
    
    @ColumnInfo(name = "check_out_time")
    val checkOutTime: Date?,
    
    @ColumnInfo(name = "status")
    val status: AttendanceStatus,
    
    @ColumnInfo(name = "notes")
    val notes: String? = null,
    
    @ColumnInfo(name = "location_latitude")
    val locationLatitude: Double? = null,
    
    @ColumnInfo(name = "location_longitude")
    val locationLongitude: Double? = null
)

/**
 * Attendance status enum
 */
enum class AttendanceStatus {
    HADIR,      // Present
    IZIN,       // Permission
    SAKIT,      // Sick
    ALFA        // Absent
}
