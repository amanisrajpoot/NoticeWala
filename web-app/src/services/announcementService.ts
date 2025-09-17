/**
 * Announcement Service for NoticeWala Web App
 * Handles announcement data fetching with refresh functionality
 */

import { apiService, endpoints } from './apiService'

export interface Announcement {
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

export interface AnnouncementsResponse {
  items: Announcement[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface CrawlerResponse {
  success: boolean
  message: string
  summary: {
    total_crawlers: number
    successful_crawls: number
    failed_crawls: number
    total_announcements_saved: number
    duration_seconds: number
  }
  results: any[]
}

class AnnouncementService {
  /**
   * Fetch announcements with optional pagination and filters
   */
  async getAnnouncements(params?: {
    page?: number
    per_page?: number
    category?: string
    source?: string
    search?: string
  }): Promise<AnnouncementsResponse> {
    const queryParams = new URLSearchParams()
    
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params?.category) queryParams.append('category', params.category)
    if (params?.source) queryParams.append('source', params.source)
    if (params?.search) queryParams.append('search', params.search)

    const url = `${endpoints.announcements.list}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiService.get<AnnouncementsResponse>(url)
  }

  /**
   * Get a specific announcement by ID
   */
  async getAnnouncement(id: string): Promise<Announcement> {
    return apiService.get<Announcement>(endpoints.announcements.detail(id))
  }

  /**
   * Refresh announcements by running crawlers and then fetching latest data
   */
  async refreshAnnouncements(): Promise<{
    crawlResult: CrawlerResponse
    announcements: AnnouncementsResponse
  }> {
    try {
      // First, run all crawlers to get fresh data
      console.log('🔄 Running crawlers to refresh data...')
      const crawlResult = await apiService.post<CrawlerResponse>(endpoints.crawlers.runAll)
      
      // Then fetch the updated announcements
      console.log('🌐 Fetching refreshed announcements...')
      const announcements = await this.getAnnouncements()
      
      return {
        crawlResult,
        announcements
      }
    } catch (error) {
      console.error('Error refreshing announcements:', error)
      throw error
    }
  }

  /**
   * Run crawlers by category
   */
  async refreshByCategory(category: string): Promise<CrawlerResponse> {
    return apiService.post<CrawlerResponse>(endpoints.crawlers.runByCategory(category))
  }

  /**
   * Get crawler statistics
   */
  async getCrawlerStats(): Promise<any> {
    return apiService.get(endpoints.crawlers.stats)
  }

  /**
   * List available crawlers
   */
  async listCrawlers(): Promise<any> {
    return apiService.get(endpoints.crawlers.list)
  }

  /**
   * Search announcements
   */
  async searchAnnouncements(query: string, filters?: {
    category?: string
    source?: string
    date_from?: string
    date_to?: string
  }): Promise<AnnouncementsResponse> {
    const params = {
      search: query,
      ...filters
    }
    return this.getAnnouncements(params)
  }

  /**
   * Get announcements by category
   */
  async getAnnouncementsByCategory(category: string): Promise<AnnouncementsResponse> {
    return this.getAnnouncements({ category })
  }

  /**
   * Get announcements by source
   */
  async getAnnouncementsBySource(source: string): Promise<AnnouncementsResponse> {
    return this.getAnnouncements({ source })
  }
}

export const announcementService = new AnnouncementService()
export default announcementService
