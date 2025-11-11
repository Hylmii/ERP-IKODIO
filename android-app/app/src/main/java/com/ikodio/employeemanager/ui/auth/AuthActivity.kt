package com.ikodio.employeemanager.ui.auth

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.ikodio.employeemanager.R
import com.ikodio.employeemanager.databinding.ActivityAuthBinding
import com.ikodio.employeemanager.ui.MainActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Authentication activity for login
 */
@AndroidEntryPoint
class AuthActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityAuthBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAuthBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
    }
    
    private fun setupViews() {
        binding.btnLogin.setOnClickListener {
            // TODO: Implement proper authentication
            // For now, directly navigate to main activity
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
            finish()
        }
    }
}
