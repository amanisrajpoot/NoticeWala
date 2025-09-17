import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material'
import { useAppSelector } from './store/hooks'
import LoginScreen from './screens/LoginScreen'
import RegisterScreen from './screens/RegisterScreen'
import HomeScreen from './screens/HomeScreen'
import AnnouncementsScreen from './screens/AnnouncementsScreen'
import ProfileScreen from './screens/ProfileScreen'

function App() {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NoticeWala
          </Typography>
          {isAuthenticated && (
            <Typography variant="body2">
              Welcome, {user?.full_name || user?.email}
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/login" element={<LoginScreen />} />
              <Route path="/register" element={<RegisterScreen />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </>
          ) : (
            <>
              <Route path="/" element={<HomeScreen />} />
              <Route path="/announcements" element={<AnnouncementsScreen />} />
              <Route path="/profile" element={<ProfileScreen />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </>
          )}
        </Routes>
      </Container>
    </Box>
  )
}

export default App
