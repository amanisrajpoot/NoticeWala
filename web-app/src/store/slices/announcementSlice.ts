import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { apiService, endpoints } from '../../services/apiService'

interface Announcement {
  id: string
  title: string
  summary?: string
  content?: string
  source: {
    id: string
    name: string
    type: string
  }
  source_url: string
  publish_date?: string
  exam_dates?: any[]
  application_deadline?: string
  eligibility?: string
  location?: any
  categories?: string[]
  tags?: string[]
  language?: string
  priority_score?: number
  confidence?: any
  is_verified: boolean
  is_duplicate: boolean
  created_at: string
  updated_at?: string
  attachments: any[]
}

interface AnnouncementsState {
  announcements: Announcement[]
  loading: boolean
  isRefreshing: boolean
  error: string | null
  total: number
  page: number
  hasMore: boolean
}

const initialState: AnnouncementsState = {
  announcements: [],
  loading: false,
  isRefreshing: false,
  error: null,
  total: 0,
  page: 1,
  hasMore: false,
}

export const fetchAnnouncements = createAsyncThunk(
  'announcements/fetchAnnouncements',
  async (params: { page?: number; per_page?: number; search?: string } = {}) => {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params.search) queryParams.append('search', params.search)

    const response = await apiService.get(`${endpoints.announcements.list}?${queryParams}`)
    return response
  }
)

export const refreshAnnouncements = createAsyncThunk(
  'announcements/refreshAnnouncements',
  async () => {
    try {
      // First run crawlers to get fresh data
      await apiService.post(endpoints.crawlers.runAll)
      
      // Then fetch the updated announcements
      const response = await apiService.get(endpoints.announcements.list)
      
      return response
    } catch (error) {
      throw error
    }
  }
)

const announcementSlice = createSlice({
  name: 'announcements',
  initialState,
  reducers: {
    clearAnnouncements: (state) => {
      state.announcements = []
      state.page = 1
      state.hasMore = false
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnnouncements.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchAnnouncements.fulfilled, (state, action) => {
        state.loading = false
        const { items, total, page } = action.payload
        
        if (page === 1) {
          state.announcements = items
        } else {
          state.announcements = [...state.announcements, ...items]
        }
        
        state.total = total
        state.page = page
        state.hasMore = items.length > 0 && state.announcements.length < total
        state.error = null
      })
      .addCase(fetchAnnouncements.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch announcements'
      })

    // Refresh announcements
    builder
      .addCase(refreshAnnouncements.pending, (state) => {
        state.isRefreshing = true
        state.error = null
      })
      .addCase(refreshAnnouncements.fulfilled, (state, action) => {
        state.isRefreshing = false
        const { items, total } = action.payload
        state.announcements = items
        state.total = total
        state.page = 1
        state.hasMore = items.length > 0 && state.announcements.length < total
      })
      .addCase(refreshAnnouncements.rejected, (state, action) => {
        state.isRefreshing = false
        state.error = action.error.message || 'Failed to refresh announcements'
      })
  },
})

export const { clearAnnouncements } = announcementSlice.actions
export default announcementSlice.reducer
