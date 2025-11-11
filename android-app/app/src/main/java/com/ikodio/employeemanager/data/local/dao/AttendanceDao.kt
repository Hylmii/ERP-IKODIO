package com.ikodio.employeemanager.data.local.dao

import androidx.room.*
import com.ikodio.employeemanager.data.local.entities.Attendance
import com.ikodio.employeemanager.data.local.entities.AttendanceStatus
import kotlinx.coroutines.flow.Flow
import java.util.Date

/**
 * Data Access Object for Attendance entity
 */
@Dao
interface AttendanceDao {
    
    @Query("SELECT * FROM attendance ORDER BY date DESC, check_in_time DESC")
    fun getAllAttendance(): Flow<List<Attendance>>
    
    @Query("SELECT * FROM attendance WHERE employee_id = :employeeId ORDER BY date DESC")
    fun getAttendanceByEmployee(employeeId: Long): Flow<List<Attendance>>
    
    @Query("SELECT * FROM attendance WHERE date = :date ORDER BY check_in_time ASC")
    fun getAttendanceByDate(date: Date): Flow<List<Attendance>>
    
    @Query("SELECT * FROM attendance WHERE employee_id = :employeeId AND date = :date")
    suspend fun getAttendanceByEmployeeAndDate(employeeId: Long, date: Date): Attendance?
    
    @Query("""
        SELECT * FROM attendance 
        WHERE employee_id = :employeeId 
        AND date BETWEEN :startDate AND :endDate 
        ORDER BY date DESC
    """)
    fun getAttendanceByDateRange(employeeId: Long, startDate: Date, endDate: Date): Flow<List<Attendance>>
    
    @Query("SELECT * FROM attendance WHERE status = :status AND date = :date")
    fun getAttendanceByStatusAndDate(status: AttendanceStatus, date: Date): Flow<List<Attendance>>
    
    @Query("SELECT COUNT(*) FROM attendance WHERE date = :date AND status = :status")
    suspend fun getAttendanceCountByStatusAndDate(date: Date, status: AttendanceStatus): Int
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAttendance(attendance: Attendance): Long
    
    @Update
    suspend fun updateAttendance(attendance: Attendance)
    
    @Delete
    suspend fun deleteAttendance(attendance: Attendance)
}
