/**
 * Authentication Service for NoticeWala Mobile App
 * Handles user authentication, registration, and token management
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService, endpoints } from './apiService';

// Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username?: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface User {
  id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'user_data';

  /**
   * Login user with credentials
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await apiService.post<TokenResponse>(
        endpoints.auth.login,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Store tokens
      await this.storeTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
      });

      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw this.handleAuthError(error);
    }
  }

  /**
   * Register new user
   */
  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await apiService.post<User>(endpoints.auth.register, userData);
      return response;
    } catch (error) {
      console.error('Registration error:', error);
      throw this.handleAuthError(error);
    }
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiService.get<User>(endpoints.auth.me);
      
      // Store user data
      await AsyncStorage.setItem(this.USER_KEY, JSON.stringify(response));
      
      return response;
    } catch (error) {
      console.error('Get current user error:', error);
      throw this.handleAuthError(error);
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    try {
      const response = await apiService.post<TokenResponse>(endpoints.auth.refresh, {
        refresh_token: refreshToken,
      });

      // Store new tokens
      await this.storeTokens({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
      });

      return response;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw this.handleAuthError(error);
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Clear stored data
      await AsyncStorage.multiRemove([
        this.ACCESS_TOKEN_KEY,
        this.REFRESH_TOKEN_KEY,
        this.USER_KEY,
      ]);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      const accessToken = await AsyncStorage.getItem(this.ACCESS_TOKEN_KEY);
      return !!accessToken;
    } catch (error) {
      console.error('Check authentication error:', error);
      return false;
    }
  }

  /**
   * Get stored access token
   */
  async getAccessToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(this.ACCESS_TOKEN_KEY);
    } catch (error) {
      console.error('Get access token error:', error);
      return null;
    }
  }

  /**
   * Get stored refresh token
   */
  async getRefreshToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(this.REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Get refresh token error:', error);
      return null;
    }
  }

  /**
   * Get stored user data
   */
  async getUserData(): Promise<User | null> {
    try {
      const userData = await AsyncStorage.getItem(this.USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Get user data error:', error);
      return null;
    }
  }

  /**
   * Store authentication tokens
   */
  private async storeTokens(tokens: AuthTokens): Promise<void> {
    try {
      await AsyncStorage.multiSet([
        [this.ACCESS_TOKEN_KEY, tokens.accessToken],
        [this.REFRESH_TOKEN_KEY, tokens.refreshToken],
      ]);
    } catch (error) {
      console.error('Store tokens error:', error);
      throw error;
    }
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Authentication failed';
      return new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network error. Please check your internet connection.');
    } else {
      // Something else happened
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: {
    first_name?: string;
    last_name?: string;
    username?: string;
  }): Promise<User> {
    try {
      const response = await apiService.put<User>(endpoints.users.updateProfile, profileData);
      
      // Update stored user data
      await AsyncStorage.setItem(this.USER_KEY, JSON.stringify(response));
      
      return response;
    } catch (error) {
      console.error('Update profile error:', error);
      throw this.handleAuthError(error);
    }
  }
}

// Create singleton instance
export const authService = new AuthService();
export default authService;
