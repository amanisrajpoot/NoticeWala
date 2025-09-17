import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { apiService } from '../../services/apiService'

interface Announcement {
  id: string
  title: string
  description: string
  source_url: string
  published_date: string
  exam_date?: string
  category: string
  source_name: string
}

interface AnnouncementsState {
  announcements: Announcement[]
  loading: boolean
  error: string | null
  total: number
  page: number
  hasMore: boolean
}

const initialState: AnnouncementsState = {
  announcements: [],
  loading: false,
  error: null,
  total: 0,
  page: 1,
  hasMore: false,
}

export const fetchAnnouncements = createAsyncThunk(
  'announcements/fetchAnnouncements',
  async (params: { page?: number; limit?: number; search?: string } = {}) => {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.search) queryParams.append('search', params.search)

    const response = await apiService.get(`/announcements?${queryParams}`)
    return response
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
        const { data, total, page } = action.payload
        
        if (page === 1) {
          state.announcements = data
        } else {
          state.announcements = [...state.announcements, ...data]
        }
        
        state.total = total
        state.page = page
        state.hasMore = data.length > 0 && state.announcements.length < total
        state.error = null
      })
      .addCase(fetchAnnouncements.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch announcements'
      })
  },
})

export const { clearAnnouncements } = announcementSlice.actions
export default announcementSlice.reducer
