import React from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { logoutUser } from '../store/slices/authSlice'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import { Person, Email, Logout, Settings } from '@mui/icons-material'

const ProfileScreen: React.FC = () => {
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)

  const handleLogout = () => {
    dispatch(logoutUser())
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profile
        </Typography>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Avatar sx={{ width: 64, height: 64, mr: 3 }}>
                <Person />
              </Avatar>
              <Box>
                <Typography variant="h5" component="h2">
                  {user?.full_name || 'User'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {user?.email}
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ mb: 2 }} />

            <List>
              <ListItem>
                <ListItemIcon>
                  <Person />
                </ListItemIcon>
                <ListItemText
                  primary="Full Name"
                  secondary={user?.full_name || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Email />
                </ListItemIcon>
                <ListItemText
                  primary="Email"
                  secondary={user?.email || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Settings />
                </ListItemIcon>
                <ListItemText
                  primary="Account Status"
                  secondary={user?.is_active ? 'Active' : 'Inactive'}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" component="h2" gutterBottom>
              Account Actions
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                color="primary"
                sx={{ mr: 2 }}
                startIcon={<Settings />}
              >
                Edit Profile
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<Logout />}
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" component="h2" gutterBottom>
              About NoticeWala
            </Typography>
            <Typography variant="body2" color="text.secondary">
              NoticeWala is your one-stop platform for exam notifications. We help students 
              stay updated with the latest announcements from universities, colleges, and 
              educational institutions across the country.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default ProfileScreen
