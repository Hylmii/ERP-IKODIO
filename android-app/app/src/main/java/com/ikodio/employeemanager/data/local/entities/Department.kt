package com.ikodio.employeemanager.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ColumnInfo

/**
 * Department entity representing department data in the database
 */
@Entity(tableName = "departments")
data class Department(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "department_name")
    val departmentName: String,
    
    @ColumnInfo(name = "department_code")
    val departmentCode: String,
    
    @ColumnInfo(name = "manager_name")
    val managerName: String
)
