package com.ikodio.employeemanager.data.local.dao

import androidx.room.*
import com.ikodio.employeemanager.data.local.entities.Department
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for Department entity
 */
@Dao
interface DepartmentDao {
    
    @Query("SELECT * FROM departments ORDER BY department_name ASC")
    fun getAllDepartments(): Flow<List<Department>>
    
    @Query("SELECT * FROM departments WHERE id = :departmentId")
    fun getDepartmentById(departmentId: Long): Flow<Department?>
    
    @Query("SELECT * FROM departments WHERE department_code = :code")
    suspend fun getDepartmentByCode(code: String): Department?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDepartment(department: Department): Long
    
    @Update
    suspend fun updateDepartment(department: Department)
    
    @Delete
    suspend fun deleteDepartment(department: Department)
    
    @Query("SELECT COUNT(*) FROM departments")
    suspend fun getDepartmentCount(): Int
}
