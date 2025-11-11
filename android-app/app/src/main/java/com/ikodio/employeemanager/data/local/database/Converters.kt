package com.ikodio.employeemanager.data.local.database

import androidx.room.TypeConverter
import com.ikodio.employeemanager.data.local.entities.AttendanceStatus
import com.ikodio.employeemanager.data.local.entities.LeaveStatus
import com.ikodio.employeemanager.data.local.entities.LeaveType
import java.util.Date

/**
 * Type converters for Room database
 */
class Converters {
    
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }
    
    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
    
    @TypeConverter
    fun fromAttendanceStatus(value: AttendanceStatus): String {
        return value.name
    }
    
    @TypeConverter
    fun toAttendanceStatus(value: String): AttendanceStatus {
        return AttendanceStatus.valueOf(value)
    }
    
    @TypeConverter
    fun fromLeaveType(value: LeaveType): String {
        return value.name
    }
    
    @TypeConverter
    fun toLeaveType(value: String): LeaveType {
        return LeaveType.valueOf(value)
    }
    
    @TypeConverter
    fun fromLeaveStatus(value: LeaveStatus): String {
        return value.name
    }
    
    @TypeConverter
    fun toLeaveStatus(value: String): LeaveStatus {
        return LeaveStatus.valueOf(value)
    }
}
