/**
 * Announcements Redux Slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, endpoints } from '@services/apiService';

// Types
export interface ExamDate {
  type: string;
  start: string;
  end?: string;
  note?: string;
}

export interface Location {
  country?: string;
  state?: string;
  city?: string;
}

export interface Source {
  id: string;
  name: string;
  type: string;
  category?: string;
  region?: string;
}

export interface Attachment {
  id: string;
  filename: string;
  file_url: string;
  file_type?: string;
  file_size?: number;
  title?: string;
}

export interface Announcement {
  id: string;
  title: string;
  summary?: string;
  content?: string;
  source: Source;
  source_url: string;
  publish_date?: string;
  exam_dates?: ExamDate[];
  application_deadline?: string;
  eligibility?: string;
  location?: Location;
  categories?: string[];
  tags?: string[];
  language: string;
  priority_score: number;
  confidence?: {
    title: number;
    dates: number;
    eligibility: number;
  };
  is_verified: boolean;
  attachments?: Attachment[];
  created_at: string;
  updated_at?: string;
}

export interface AnnouncementListResponse {
  items: Announcement[];
  total: number;
  skip: number;
  limit: number;
}

export interface AnnouncementFilters {
  category?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  skip?: number;
  limit?: number;
}

interface AnnouncementState {
  announcements: Announcement[];
  currentAnnouncement: Announcement | null;
  categories: string[];
  sources: Source[];
  filters: AnnouncementFilters;
  totalCount: number;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  hasMore: boolean;
}

const initialState: AnnouncementState = {
  announcements: [],
  currentAnnouncement: null,
  categories: [],
  sources: [],
  filters: {
    skip: 0,
    limit: 20,
    sort_by: 'created_at',
    sort_order: 'desc',
  },
  totalCount: 0,
  isLoading: false,
  isRefreshing: false,
  error: null,
  hasMore: true,
};

// Async thunks
export const fetchAnnouncements = createAsyncThunk(
  'announcements/fetchAnnouncements',
  async (filters: AnnouncementFilters, { rejectWithValue }) => {
    try {
      const params = new URLSearchParams();
      
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
      if (filters.category) params.append('category', filters.category);
      if (filters.search) params.append('search', filters.search);
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);

      const response = await apiService.get<AnnouncementListResponse>(
        `${endpoints.announcements.list}?${params.toString()}`
      );
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch announcements');
    }
  }
);

export const fetchAnnouncementById = createAsyncThunk(
  'announcements/fetchAnnouncementById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await apiService.get<Announcement>(
        endpoints.announcements.detail(id)
      );
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch announcement');
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'announcements/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get<{ categories: string[] }>(
        endpoints.announcements.categories
      );
      return response.categories;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch categories');
    }
  }
);

export const fetchSources = createAsyncThunk(
  'announcements/fetchSources',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get<{ sources: Source[] }>(
        endpoints.announcements.sources
      );
      return response.sources;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch sources');
    }
  }
);

export const refreshAnnouncements = createAsyncThunk(
  'announcements/refreshAnnouncements',
  async (_, { rejectWithValue }) => {
    try {
      // First run crawlers to get fresh data
      await apiService.post(endpoints.crawlers.runAll);
      
      // Then fetch the updated announcements
      const response = await apiService.get<AnnouncementListResponse>(
        endpoints.announcements.list
      );
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to refresh announcements');
    }
  }
);

const announcementSlice = createSlice({
  name: 'announcements',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<AnnouncementFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        skip: 0,
        limit: 20,
        sort_by: 'created_at',
        sort_order: 'desc',
      };
    },
    clearAnnouncements: (state) => {
      state.announcements = [];
      state.totalCount = 0;
      state.hasMore = true;
      state.filters.skip = 0;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentAnnouncement: (state) => {
      state.currentAnnouncement = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch announcements
    builder
      .addCase(fetchAnnouncements.pending, (state, action) => {
        state.isLoading = true;
        state.error = null;
        
        // If it's a refresh (skip = 0), set refreshing flag
        if (action.meta.arg.skip === 0) {
          state.isRefreshing = true;
        }
      })
      .addCase(fetchAnnouncements.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isRefreshing = false;
        
        const { items, total, skip } = action.payload;
        
        if (skip === 0) {
          // Fresh load
          state.announcements = items;
        } else {
          // Load more
          state.announcements = [...state.announcements, ...items];
        }
        
        state.totalCount = total;
        state.hasMore = state.announcements.length < total;
        state.filters.skip = skip + items.length;
      })
      .addCase(fetchAnnouncements.rejected, (state, action) => {
        state.isLoading = false;
        state.isRefreshing = false;
        state.error = action.payload as string;
      });

    // Fetch announcement by ID
    builder
      .addCase(fetchAnnouncementById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAnnouncementById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentAnnouncement = action.payload;
      })
      .addCase(fetchAnnouncementById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch categories
    builder
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Fetch sources
    builder
      .addCase(fetchSources.fulfilled, (state, action) => {
        state.sources = action.payload;
      })
      .addCase(fetchSources.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Refresh announcements
    builder
      .addCase(refreshAnnouncements.pending, (state) => {
        state.isRefreshing = true;
        state.error = null;
      })
      .addCase(refreshAnnouncements.fulfilled, (state, action) => {
        state.isRefreshing = false;
        const { items, total } = action.payload;
        state.announcements = items;
        state.totalCount = total;
        state.hasMore = state.announcements.length < total;
        state.filters.skip = items.length;
      })
      .addCase(refreshAnnouncements.rejected, (state, action) => {
        state.isRefreshing = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setFilters,
  clearFilters,
  clearAnnouncements,
  clearError,
  clearCurrentAnnouncement,
} = announcementSlice.actions;

export default announcementSlice.reducer;
