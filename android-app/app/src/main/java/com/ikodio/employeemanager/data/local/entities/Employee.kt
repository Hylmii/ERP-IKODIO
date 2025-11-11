package com.ikodio.employeemanager.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ColumnInfo
import java.util.Date

/**
 * Employee entity representing employee data in the database
 */
@Entity(tableName = "employees")
data class Employee(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "employee_id")
    val employeeId: String,
    
    @ColumnInfo(name = "full_name")
    val fullName: String,
    
    @ColumnInfo(name = "email")
    val email: String,
    
    @ColumnInfo(name = "phone_number")
    val phoneNumber: String,
    
    @ColumnInfo(name = "position")
    val position: String,
    
    @ColumnInfo(name = "department_id")
    val departmentId: Long,
    
    @ColumnInfo(name = "salary")
    val salary: Double,
    
    @ColumnInfo(name = "date_of_joining")
    val dateOfJoining: Date,
    
    @ColumnInfo(name = "address")
    val address: String,
    
    @ColumnInfo(name = "photo_uri")
    val photoUri: String? = null,
    
    @ColumnInfo(name = "is_active")
    val isActive: Boolean = true,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    @ColumnInfo(name = "updated_at")
    val updatedAt: Date = Date()
)
