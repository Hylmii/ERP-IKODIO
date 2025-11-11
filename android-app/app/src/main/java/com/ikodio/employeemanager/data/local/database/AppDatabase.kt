package com.ikodio.employeemanager.data.local.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.ikodio.employeemanager.data.local.dao.*
import com.ikodio.employeemanager.data.local.entities.*

/**
 * Room Database class for Employee Manager app
 */
@Database(
    entities = [
        Employee::class,
        Department::class,
        Attendance::class,
        Leave::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun employeeDao(): EmployeeDao
    abstract fun departmentDao(): DepartmentDao
    abstract fun attendanceDao(): AttendanceDao
    abstract fun leaveDao(): LeaveDao
    
    companion object {
        private const val DATABASE_NAME = "employee_manager_db"
        
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    DATABASE_NAME
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
