import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Chip,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Search } from '@mui/icons-material'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { fetchAnnouncements, clearAnnouncements } from '../store/slices/announcementSlice'

const AnnouncementsScreen: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const dispatch = useAppDispatch()
  const { announcements, loading, error, hasMore } = useAppSelector((state) => state.announcements)

  useEffect(() => {
    dispatch(clearAnnouncements())
    dispatch(fetchAnnouncements({ page: 1, limit: 10 }))
  }, [dispatch])

  const handleSearch = () => {
    dispatch(clearAnnouncements())
    dispatch(fetchAnnouncements({ page: 1, limit: 10, search: searchTerm }))
  }

  const handleLoadMore = () => {
    dispatch(fetchAnnouncements({ page: 1, limit: 10, search: searchTerm }))
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Exam Announcements
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Stay updated with the latest exam notifications from universities and institutions
        </Typography>

        {/* Search */}
        <Box sx={{ mt: 3, mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search announcements..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch()
              }
            }}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            sx={{ mt: 2 }}
            disabled={loading}
          >
            Search
          </Button>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading && announcements.length === 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Announcements */}
        {announcements.length > 0 && (
          <Box>
            {announcements.map((announcement) => (
              <Card key={announcement.id} sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" component="h2" gutterBottom>
                    {announcement.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                    {announcement.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip 
                      label={announcement.category} 
                      color="primary" 
                      variant="outlined" 
                      size="small"
                    />
                    <Chip 
                      label={announcement.source_name} 
                      color="secondary" 
                      variant="outlined" 
                      size="small"
                    />
                    {announcement.exam_date && (
                      <Chip 
                        label={`Exam: ${new Date(announcement.exam_date).toLocaleDateString()}`} 
                        color="success" 
                        variant="outlined" 
                        size="small"
                      />
                    )}
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      Published: {new Date(announcement.published_date).toLocaleDateString()}
                    </Typography>
                    <Button
                      size="small"
                      href={announcement.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Source
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))}

            {/* Load More */}
            {hasMore && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={handleLoadMore}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                >
                  Load More
                </Button>
              </Box>
            )}
          </Box>
        )}

        {/* No Results */}
        {!loading && announcements.length === 0 && !error && (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No announcements found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your search terms or check back later for new announcements
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  )
}

export default AnnouncementsScreen
