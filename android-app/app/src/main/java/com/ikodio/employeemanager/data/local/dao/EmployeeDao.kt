package com.ikodio.employeemanager.data.local.dao

import androidx.room.*
import com.ikodio.employeemanager.data.local.entities.Employee
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for Employee entity
 */
@Dao
interface EmployeeDao {
    
    @Query("SELECT * FROM employees ORDER BY full_name ASC")
    fun getAllEmployees(): Flow<List<Employee>>
    
    @Query("SELECT * FROM employees WHERE is_active = 1 ORDER BY full_name ASC")
    fun getActiveEmployees(): Flow<List<Employee>>
    
    @Query("SELECT * FROM employees WHERE id = :employeeId")
    fun getEmployeeById(employeeId: Long): Flow<Employee?>
    
    @Query("SELECT * FROM employees WHERE employee_id = :employeeId")
    suspend fun getEmployeeByEmployeeId(employeeId: String): Employee?
    
    @Query("SELECT * FROM employees WHERE department_id = :departmentId ORDER BY full_name ASC")
    fun getEmployeesByDepartment(departmentId: Long): Flow<List<Employee>>
    
    @Query("""
        SELECT * FROM employees 
        WHERE full_name LIKE '%' || :query || '%' 
        OR email LIKE '%' || :query || '%' 
        OR employee_id LIKE '%' || :query || '%'
        ORDER BY full_name ASC
    """)
    fun searchEmployees(query: String): Flow<List<Employee>>
    
    @Query("SELECT COUNT(*) FROM employees WHERE is_active = 1")
    fun getActiveEmployeeCount(): Flow<Int>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEmployee(employee: Employee): Long
    
    @Update
    suspend fun updateEmployee(employee: Employee)
    
    @Delete
    suspend fun deleteEmployee(employee: Employee)
    
    @Query("UPDATE employees SET is_active = 0 WHERE id = :employeeId")
    suspend fun deactivateEmployee(employeeId: Long)
    
    @Query("UPDATE employees SET is_active = 1 WHERE id = :employeeId")
    suspend fun activateEmployee(employeeId: Long)
}
