import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { authService } from '@services/authService'
import { useAuthStore } from '@store/authStore'
import { FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi'
import api from '@services/api'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  // Fetch CSRF token on component mount
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        // Use axios directly to avoid error interceptor toast
        await api.get('/auth/csrf/', { 
          headers: { 'X-Skip-Error-Toast': 'true' } 
        })
      } catch (error) {
        // Silently fail - CSRF token will be set when it's fetched successfully
        console.debug('CSRF token fetch (initial attempt):', error)
      }
    }
    fetchCsrfToken()
  }, [])

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const response = await authService.login(data)
      setAuth(response.user, response.tokens)
      toast.success(`Welcome back, ${response.user.full_name}!`)
      navigate('/')
    } catch (error: unknown) {
      const errorMessage = error instanceof Error && 'response' in error 
        ? (error as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message 
        : 'Login failed. Please try again.'
      toast.error(errorMessage || 'Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="email" className="form-label">
          Email Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiMail className="h-5 w-5 text-gray-400" />
          </div>
          <input
            {...register('email')}
            id="email"
            type="email"
            autoComplete="email"
            className="form-input pl-10"
            placeholder="you@example.com"
          />
        </div>
        {errors.email && <p className="form-error">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="password" className="form-label">
          Password
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiLock className="h-5 w-5 text-gray-400" />
          </div>
          <input
            {...register('password')}
            id="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="current-password"
            className="form-input pl-10 pr-10"
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showPassword ? (
              <FiEyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            ) : (
              <FiEye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            )}
          </button>
        </div>
        {errors.password && <p className="form-error">{errors.password.message}</p>}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            id="remember-me"
            name="remember-me"
            type="checkbox"
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
            Remember me
          </label>
        </div>

        <div className="text-sm">
          <a href="#" className="font-medium text-primary-600 hover:text-primary-500">
            Forgot password?
          </a>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full btn-primary"
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Signing in...
          </span>
        ) : (
          'Sign in'
        )}
      </button>
    </form>
  )
}
