package com.ikodio.employeemanager.di

import android.content.Context
import com.ikodio.employeemanager.data.local.database.AppDatabase
import com.ikodio.employeemanager.data.local.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Hilt module for providing database and DAO dependencies
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideAppDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return AppDatabase.getInstance(context)
    }
    
    @Provides
    @Singleton
    fun provideEmployeeDao(database: AppDatabase): EmployeeDao {
        return database.employeeDao()
    }
    
    @Provides
    @Singleton
    fun provideDepartmentDao(database: AppDatabase): DepartmentDao {
        return database.departmentDao()
    }
    
    @Provides
    @Singleton
    fun provideAttendanceDao(database: AppDatabase): AttendanceDao {
        return database.attendanceDao()
    }
    
    @Provides
    @Singleton
    fun provideLeaveDao(database: AppDatabase): LeaveDao {
        return database.leaveDao()
    }
}
