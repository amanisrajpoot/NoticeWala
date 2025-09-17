/**
 * Notifications Redux Slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, endpoints } from '@services/apiService';

// Types
export interface NotificationData {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  status: string;
  created_at: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
}

export interface NotificationSettings {
  push_enabled: boolean;
  email_enabled: boolean;
  quiet_hours?: {
    enabled: boolean;
    start_time: string;
    end_time: string;
    timezone: string;
  };
  priority_threshold: number;
  categories?: string[];
  sources?: string[];
}

export interface NotificationListResponse {
  items: NotificationData[];
  total: number;
}

interface NotificationState {
  notifications: NotificationData[];
  unreadCount: number;
  settings: NotificationSettings | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  hasMore: boolean;
  totalCount: number;
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  settings: null,
  isLoading: false,
  isRefreshing: false,
  error: null,
  hasMore: true,
  totalCount: 0,
};

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchNotifications',
  async (
    { skip = 0, limit = 20, status }: { skip?: number; limit?: number; status?: string },
    { rejectWithValue }
  ) => {
    try {
      const params = new URLSearchParams();
      params.append('skip', skip.toString());
      params.append('limit', limit.toString());
      if (status) params.append('status_filter', status);

      const response = await apiService.get<NotificationData[]>(
        `${endpoints.notifications.list}?${params.toString()}`
      );
      
      return {
        items: response,
        total: response.length,
        skip,
        limit,
      };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch notifications');
    }
  }
);

export const markNotificationRead = createAsyncThunk(
  'notifications/markNotificationRead',
  async (notificationId: string, { rejectWithValue }) => {
    try {
      await apiService.put(endpoints.notifications.read(notificationId));
      return notificationId;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to mark notification as read');
    }
  }
);

export const deleteNotification = createAsyncThunk(
  'notifications/deleteNotification',
  async (notificationId: string, { rejectWithValue }) => {
    try {
      await apiService.delete(endpoints.notifications.delete(notificationId));
      return notificationId;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete notification');
    }
  }
);

export const fetchNotificationSettings = createAsyncThunk(
  'notifications/fetchNotificationSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get<NotificationSettings>(
        endpoints.notifications.settings
      );
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch notification settings');
    }
  }
);

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<NotificationData>) => {
      state.notifications.unshift(action.payload);
      state.totalCount += 1;
      
      // Update unread count if notification is not read
      if (!action.payload.opened_at) {
        state.unreadCount += 1;
      }
    },
    markAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.opened_at) {
        notification.opened_at = new Date().toISOString();
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
      state.totalCount = 0;
      state.hasMore = true;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateUnreadCount: (state, action: PayloadAction<number>) => {
      state.unreadCount = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch notifications
    builder
      .addCase(fetchNotifications.pending, (state, action) => {
        state.isLoading = true;
        state.error = null;
        
        // If it's a refresh (skip = 0), set refreshing flag
        if (action.meta.arg.skip === 0) {
          state.isRefreshing = true;
        }
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isRefreshing = false;
        
        const { items, total, skip } = action.payload;
        
        if (skip === 0) {
          // Fresh load
          state.notifications = items;
        } else {
          // Load more
          state.notifications = [...state.notifications, ...items];
        }
        
        state.totalCount = total;
        state.hasMore = state.notifications.length < total;
        
        // Calculate unread count
        state.unreadCount = items.filter(n => !n.opened_at).length;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.isLoading = false;
        state.isRefreshing = false;
        state.error = action.payload as string;
      });

    // Mark notification as read
    builder
      .addCase(markNotificationRead.fulfilled, (state, action) => {
        const notification = state.notifications.find(n => n.id === action.payload);
        if (notification && !notification.opened_at) {
          notification.opened_at = new Date().toISOString();
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      })
      .addCase(markNotificationRead.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Delete notification
    builder
      .addCase(deleteNotification.fulfilled, (state, action) => {
        const notification = state.notifications.find(n => n.id === action.payload);
        if (notification) {
          // Remove from notifications array
          state.notifications = state.notifications.filter(n => n.id !== action.payload);
          state.totalCount = Math.max(0, state.totalCount - 1);
          
          // Update unread count if notification was unread
          if (!notification.opened_at) {
            state.unreadCount = Math.max(0, state.unreadCount - 1);
          }
        }
      })
      .addCase(deleteNotification.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Fetch notification settings
    builder
      .addCase(fetchNotificationSettings.fulfilled, (state, action) => {
        state.settings = action.payload;
      })
      .addCase(fetchNotificationSettings.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const {
  addNotification,
  markAsRead,
  clearNotifications,
  clearError,
  updateUnreadCount,
} = notificationSlice.actions;

export default notificationSlice.reducer;
