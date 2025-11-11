package com.ikodio.employeemanager.data.repository

import com.ikodio.employeemanager.data.local.dao.EmployeeDao
import com.ikodio.employeemanager.data.local.entities.Employee
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for Employee data operations
 */
@Singleton
class EmployeeRepository @Inject constructor(
    private val employeeDao: EmployeeDao
) {
    
    fun getAllEmployees(): Flow<List<Employee>> = employeeDao.getAllEmployees()
    
    fun getActiveEmployees(): Flow<List<Employee>> = employeeDao.getActiveEmployees()
    
    fun getEmployeeById(employeeId: Long): Flow<Employee?> = employeeDao.getEmployeeById(employeeId)
    
    suspend fun getEmployeeByEmployeeId(employeeId: String): Employee? = 
        employeeDao.getEmployeeByEmployeeId(employeeId)
    
    fun getEmployeesByDepartment(departmentId: Long): Flow<List<Employee>> = 
        employeeDao.getEmployeesByDepartment(departmentId)
    
    fun searchEmployees(query: String): Flow<List<Employee>> = 
        employeeDao.searchEmployees(query)
    
    fun getActiveEmployeeCount(): Flow<Int> = employeeDao.getActiveEmployeeCount()
    
    suspend fun insertEmployee(employee: Employee): Long = 
        employeeDao.insertEmployee(employee)
    
    suspend fun updateEmployee(employee: Employee) = 
        employeeDao.updateEmployee(employee)
    
    suspend fun deleteEmployee(employee: Employee) = 
        employeeDao.deleteEmployee(employee)
    
    suspend fun deactivateEmployee(employeeId: Long) = 
        employeeDao.deactivateEmployee(employeeId)
    
    suspend fun activateEmployee(employeeId: Long) = 
        employeeDao.activateEmployee(employeeId)
}
