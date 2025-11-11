package com.ikodio.employeemanager

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for Employee Manager
 * Annotated with @HiltAndroidApp to enable Hilt dependency injection
 */
@HiltAndroidApp
class EmployeeManagerApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
    }
}
