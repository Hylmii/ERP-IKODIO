package com.ikodio.employeemanager.ui.leave

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.ikodio.employeemanager.databinding.FragmentLeaveBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LeaveFragment : Fragment() {
    
    private var _binding: FragmentLeaveBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLeaveBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
