/**
 * Subscriptions Redux Slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, endpoints } from '@services/apiService';

// Types
export interface SubscriptionFilters {
  categories?: string[];
  keywords?: string[];
  locations?: string[];
  sources?: string[];
  date_range?: {
    from: string;
    to: string;
  };
  min_priority?: number;
}

export interface QuietHours {
  enabled: boolean;
  start_time: string;
  end_time: string;
  timezone: string;
}

export interface Subscription {
  id: string;
  name: string;
  filters: SubscriptionFilters;
  is_active: boolean;
  notification_enabled: boolean;
  priority_threshold: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateSubscriptionData {
  name: string;
  filters: SubscriptionFilters;
  notification_enabled?: boolean;
  quiet_hours?: QuietHours;
  priority_threshold?: number;
}

export interface UpdateSubscriptionData {
  name?: string;
  filters?: SubscriptionFilters;
  is_active?: boolean;
  notification_enabled?: boolean;
  quiet_hours?: QuietHours;
  priority_threshold?: number;
}

interface SubscriptionState {
  subscriptions: Subscription[];
  currentSubscription: Subscription | null;
  isLoading: boolean;
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  error: string | null;
}

const initialState: SubscriptionState = {
  subscriptions: [],
  currentSubscription: null,
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,
  error: null,
};

// Async thunks
export const fetchSubscriptions = createAsyncThunk(
  'subscriptions/fetchSubscriptions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get<Subscription[]>(endpoints.subscriptions.list);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch subscriptions');
    }
  }
);

export const createSubscription = createAsyncThunk(
  'subscriptions/createSubscription',
  async (subscriptionData: CreateSubscriptionData, { rejectWithValue }) => {
    try {
      const response = await apiService.post<Subscription>(
        endpoints.subscriptions.create,
        subscriptionData
      );
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to create subscription');
    }
  }
);

export const updateSubscription = createAsyncThunk(
  'subscriptions/updateSubscription',
  async (
    { id, data }: { id: string; data: UpdateSubscriptionData },
    { rejectWithValue }
  ) => {
    try {
      const response = await apiService.put<Subscription>(
        endpoints.subscriptions.update(id),
        data
      );
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update subscription');
    }
  }
);

export const deleteSubscription = createAsyncThunk(
  'subscriptions/deleteSubscription',
  async (id: string, { rejectWithValue }) => {
    try {
      await apiService.delete(endpoints.subscriptions.delete(id));
      return id;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete subscription');
    }
  }
);

const subscriptionSlice = createSlice({
  name: 'subscriptions',
  initialState,
  reducers: {
    setCurrentSubscription: (state, action: PayloadAction<Subscription | null>) => {
      state.currentSubscription = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearSubscriptions: (state) => {
      state.subscriptions = [];
      state.currentSubscription = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch subscriptions
    builder
      .addCase(fetchSubscriptions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSubscriptions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.subscriptions = action.payload;
      })
      .addCase(fetchSubscriptions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create subscription
    builder
      .addCase(createSubscription.pending, (state) => {
        state.isCreating = true;
        state.error = null;
      })
      .addCase(createSubscription.fulfilled, (state, action) => {
        state.isCreating = false;
        state.subscriptions.push(action.payload);
        state.currentSubscription = action.payload;
      })
      .addCase(createSubscription.rejected, (state, action) => {
        state.isCreating = false;
        state.error = action.payload as string;
      });

    // Update subscription
    builder
      .addCase(updateSubscription.pending, (state) => {
        state.isUpdating = true;
        state.error = null;
      })
      .addCase(updateSubscription.fulfilled, (state, action) => {
        state.isUpdating = false;
        const index = state.subscriptions.findIndex(sub => sub.id === action.payload.id);
        if (index !== -1) {
          state.subscriptions[index] = action.payload;
        }
        if (state.currentSubscription?.id === action.payload.id) {
          state.currentSubscription = action.payload;
        }
      })
      .addCase(updateSubscription.rejected, (state, action) => {
        state.isUpdating = false;
        state.error = action.payload as string;
      });

    // Delete subscription
    builder
      .addCase(deleteSubscription.pending, (state) => {
        state.isDeleting = true;
        state.error = null;
      })
      .addCase(deleteSubscription.fulfilled, (state, action) => {
        state.isDeleting = false;
        state.subscriptions = state.subscriptions.filter(sub => sub.id !== action.payload);
        if (state.currentSubscription?.id === action.payload) {
          state.currentSubscription = null;
        }
      })
      .addCase(deleteSubscription.rejected, (state, action) => {
        state.isDeleting = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setCurrentSubscription,
  clearError,
  clearSubscriptions,
} = subscriptionSlice.actions;

export default subscriptionSlice.reducer;
