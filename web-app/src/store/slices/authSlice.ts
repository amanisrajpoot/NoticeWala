import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiService } from '../../services/apiService'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,
}

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }) => {
    const response = await apiService.post('/auth/login', credentials)
    localStorage.setItem('access_token', response.access_token)
    return response
  }
)

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: { email: string; password: string; full_name: string }) => {
    const response = await apiService.post('/auth/register', userData)
    return response
  }
)

export const logoutUser = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('access_token')
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false
        state.isAuthenticated = true
        state.token = action.payload.access_token
        state.user = action.payload.user
        state.error = null
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false
        state.isAuthenticated = false
        state.error = action.error.message || 'Login failed'
      })
      // Register
      .addCase(registerUser.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Registration failed'
      })
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
      })
  },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer
