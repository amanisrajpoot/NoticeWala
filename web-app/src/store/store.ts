import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import announcementSlice from './slices/announcementSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    announcements: announcementSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
