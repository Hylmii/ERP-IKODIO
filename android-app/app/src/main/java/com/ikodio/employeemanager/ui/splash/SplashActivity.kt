package com.ikodio.employeemanager.ui.splash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.ikodio.employeemanager.R
import com.ikodio.employeemanager.ui.auth.AuthActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Splash screen activity shown on app launch
 */
@AndroidEntryPoint
class SplashActivity : AppCompatActivity() {
    
    private companion object {
        const val SPLASH_DELAY = 2000L // 2 seconds
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)
        
        // Navigate to auth screen after delay
        Handler(Looper.getMainLooper()).postDelayed({
            startActivity(Intent(this, AuthActivity::class.java))
            finish()
        }, SPLASH_DELAY)
    }
}
