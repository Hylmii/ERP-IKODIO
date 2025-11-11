package com.ikodio.employeemanager.data.repository

import com.ikodio.employeemanager.data.local.dao.DepartmentDao
import com.ikodio.employeemanager.data.local.entities.Department
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for Department data operations
 */
@Singleton
class DepartmentRepository @Inject constructor(
    private val departmentDao: DepartmentDao
) {
    
    fun getAllDepartments(): Flow<List<Department>> = departmentDao.getAllDepartments()
    
    fun getDepartmentById(departmentId: Long): Flow<Department?> = 
        departmentDao.getDepartmentById(departmentId)
    
    suspend fun getDepartmentByCode(code: String): Department? = 
        departmentDao.getDepartmentByCode(code)
    
    suspend fun insertDepartment(department: Department): Long = 
        departmentDao.insertDepartment(department)
    
    suspend fun updateDepartment(department: Department) = 
        departmentDao.updateDepartment(department)
    
    suspend fun deleteDepartment(department: Department) = 
        departmentDao.deleteDepartment(department)
    
    suspend fun getDepartmentCount(): Int = departmentDao.getDepartmentCount()
}
