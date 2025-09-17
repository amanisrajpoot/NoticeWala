import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
} from '@mui/material'
import { School, Notifications, Search, Person } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { fetchAnnouncements } from '../store/slices/announcementSlice'

const HomeScreen: React.FC = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)
  const { announcements, loading } = useAppSelector((state) => state.announcements)

  useEffect(() => {
    dispatch(fetchAnnouncements({ limit: 5 }))
  }, [dispatch])

  const quickActions = [
    {
      title: 'View Announcements',
      description: 'Browse all exam announcements',
      icon: <School sx={{ fontSize: 40 }} />,
      color: 'primary',
      onClick: () => navigate('/announcements'),
    },
    {
      title: 'Search Exams',
      description: 'Find specific exam information',
      icon: <Search sx={{ fontSize: 40 }} />,
      color: 'secondary',
      onClick: () => navigate('/announcements'),
    },
    {
      title: 'Notifications',
      description: 'Manage your notifications',
      icon: <Notifications sx={{ fontSize: 40 }} />,
      color: 'success',
      onClick: () => {},
    },
    {
      title: 'Profile',
      description: 'Update your profile',
      icon: <Person sx={{ fontSize: 40 }} />,
      color: 'info',
      onClick: () => navigate('/profile'),
    },
  ]

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {user?.full_name || 'Student'}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Stay updated with the latest exam notifications
        </Typography>

        {/* Quick Actions */}
        <Box sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={3}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                    },
                  }}
                  onClick={action.onClick}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ color: `${action.color}.main`, mb: 2 }}>
                      {action.icon}
                    </Box>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {action.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {action.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Recent Announcements */}
        <Box sx={{ mt: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" component="h2">
              Recent Announcements
            </Typography>
            <Button 
              variant="outlined" 
              onClick={() => navigate('/announcements')}
            >
              View All
            </Button>
          </Box>

          {loading ? (
            <Typography>Loading announcements...</Typography>
          ) : announcements.length > 0 ? (
            <Grid container spacing={3}>
              {announcements.slice(0, 3).map((announcement) => (
                <Grid item xs={12} md={4} key={announcement.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {announcement.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {announcement.description.length > 100 
                          ? `${announcement.description.substring(0, 100)}...`
                          : announcement.description
                        }
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip 
                          label={announcement.category} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                        <Chip 
                          label={announcement.source_name} 
                          size="small" 
                          color="secondary" 
                          variant="outlined" 
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Published: {new Date(announcement.published_date).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  No announcements found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Check back later for new exam notifications
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Container>
  )
}

export default HomeScreen
