package com.ikodio.employeemanager.data.local.dao

import androidx.room.*
import com.ikodio.employeemanager.data.local.entities.Leave
import com.ikodio.employeemanager.data.local.entities.LeaveStatus
import com.ikodio.employeemanager.data.local.entities.LeaveType
import kotlinx.coroutines.flow.Flow
import java.util.Date

/**
 * Data Access Object for Leave entity
 */
@Dao
interface LeaveDao {
    
    @Query("SELECT * FROM leaves ORDER BY created_at DESC")
    fun getAllLeaves(): Flow<List<Leave>>
    
    @Query("SELECT * FROM leaves WHERE employee_id = :employeeId ORDER BY created_at DESC")
    fun getLeavesByEmployee(employeeId: Long): Flow<List<Leave>>
    
    @Query("SELECT * FROM leaves WHERE id = :leaveId")
    fun getLeaveById(leaveId: Long): Flow<Leave?>
    
    @Query("SELECT * FROM leaves WHERE status = :status ORDER BY created_at DESC")
    fun getLeavesByStatus(status: LeaveStatus): Flow<List<Leave>>
    
    @Query("""
        SELECT * FROM leaves 
        WHERE employee_id = :employeeId 
        AND status = :status 
        ORDER BY created_at DESC
    """)
    fun getLeavesByEmployeeAndStatus(employeeId: Long, status: LeaveStatus): Flow<List<Leave>>
    
    @Query("""
        SELECT * FROM leaves 
        WHERE employee_id = :employeeId 
        AND leave_type = :leaveType 
        ORDER BY created_at DESC
    """)
    fun getLeavesByEmployeeAndType(employeeId: Long, leaveType: LeaveType): Flow<List<Leave>>
    
    @Query("SELECT COUNT(*) FROM leaves WHERE status = :status")
    suspend fun getLeaveCountByStatus(status: LeaveStatus): Int
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertLeave(leave: Leave): Long
    
    @Update
    suspend fun updateLeave(leave: Leave)
    
    @Delete
    suspend fun deleteLeave(leave: Leave)
}
