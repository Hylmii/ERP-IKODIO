import api from './api'
import { LoginCredentials, LoginResponse, User } from '@/types/common'

export const authService = {
  // Login
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await api.post('/auth/login/', credentials)
    return response.data
  },

  // Logout
  logout: async (): Promise<void> => {
    await api.post('/auth/logout/')
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me/')
    return response.data
  },

  // Update profile
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.patch('/auth/profile/', data)
    return response.data
  },

  // Change password
  changePassword: async (data: {
    old_password: string
    new_password: string
  }): Promise<void> => {
    await api.post('/auth/change-password/', data)
  },

  // Request password reset
  requestPasswordReset: async (email: string): Promise<void> => {
    await api.post('/auth/password-reset/', { email })
  },

  // Confirm password reset
  confirmPasswordReset: async (data: {
    token: string
    password: string
  }): Promise<void> => {
    await api.post('/auth/password-reset/confirm/', data)
  },
}
