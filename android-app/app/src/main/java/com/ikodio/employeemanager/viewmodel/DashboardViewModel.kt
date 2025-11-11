package com.ikodio.employeemanager.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import com.ikodio.employeemanager.data.repository.EmployeeRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

/**
 * ViewModel for Dashboard
 */
@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val employeeRepository: EmployeeRepository
) : ViewModel() {
    
    val activeEmployeeCount: LiveData<Int> = employeeRepository.getActiveEmployeeCount().asLiveData()
}
