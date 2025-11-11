package com.ikodio.employeemanager.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.ikodio.employeemanager.databinding.FragmentDashboardBinding
import com.ikodio.employeemanager.viewmodel.DashboardViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Dashboard fragment showing statistics and quick actions
 */
@AndroidEntryPoint
class DashboardFragment : Fragment() {
    
    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: DashboardViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupObservers()
    }
    
    private fun setupObservers() {
        viewModel.activeEmployeeCount.observe(viewLifecycleOwner) { count ->
            binding.tvActiveEmployees.text = count.toString()
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
