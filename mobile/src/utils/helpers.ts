/**
 * Helper utilities for NoticeWala Mobile App
 */

import { Platform } from 'react-native';

/**
 * Format date for display
 */
export const formatDate = (date: string | Date, format: 'short' | 'long' | 'relative' = 'short'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid date';
  }

  const now = new Date();
  const diffInMs = now.getTime() - dateObj.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));

  if (format === 'relative') {
    if (diffInMinutes < 1) {
      return 'Just now';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else if (diffInDays < 7) {
      return `${diffInDays}d ago`;
    } else if (diffInDays < 30) {
      const weeks = Math.floor(diffInDays / 7);
      return `${weeks}w ago`;
    } else {
      const months = Math.floor(diffInDays / 30);
      return `${months}mo ago`;
    }
  }

  const options: Intl.DateTimeFormatOptions = {
    year: format === 'long' ? 'numeric' : '2-digit',
    month: format === 'long' ? 'long' : 'short',
    day: 'numeric',
  };

  return dateObj.toLocaleDateString('en-US', options);
};

/**
 * Format time for display
 */
export const formatTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid time';
  }

  return dateObj.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
};

/**
 * Get time until deadline
 */
export const getTimeUntilDeadline = (deadline: string | Date): string => {
  const deadlineDate = typeof deadline === 'string' ? new Date(deadline) : deadline;
  const now = new Date();
  
  if (isNaN(deadlineDate.getTime())) {
    return 'Invalid deadline';
  }

  const diffInMs = deadlineDate.getTime() - now.getTime();
  
  if (diffInMs < 0) {
    return 'Expired';
  }

  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  const diffInHours = Math.floor((diffInMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const diffInMinutes = Math.floor((diffInMs % (1000 * 60 * 60)) / (1000 * 60));

  if (diffInDays > 0) {
    return `${diffInDays}d ${diffInHours}h`;
  } else if (diffInHours > 0) {
    return `${diffInHours}h ${diffInMinutes}m`;
  } else {
    return `${diffInMinutes}m`;
  }
};

/**
 * Check if deadline is urgent (less than 7 days)
 */
export const isDeadlineUrgent = (deadline: string | Date): boolean => {
  const deadlineDate = typeof deadline === 'string' ? new Date(deadline) : deadline;
  const now = new Date();
  
  if (isNaN(deadlineDate.getTime())) {
    return false;
  }

  const diffInMs = deadlineDate.getTime() - now.getTime();
  const diffInDays = diffInMs / (1000 * 60 * 60 * 24);
  
  return diffInDays > 0 && diffInDays <= 7;
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number, suffix: string = '...'): string => {
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength - suffix.length) + suffix;
};

/**
 * Capitalize first letter of each word
 */
export const capitalizeWords = (text: string): string => {
  return text.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

/**
 * Get category display name
 */
export const getCategoryDisplayName = (category: string): string => {
  const categoryMap: Record<string, string> = {
    government: 'Government',
    competitive: 'Competitive',
    engineering: 'Engineering',
    medical: 'Medical',
    scholarship: 'Scholarship',
    school: 'School',
    university: 'University',
    certification: 'Certification',
  };
  
  return categoryMap[category] || capitalizeWords(category);
};

/**
 * Get category color
 */
export const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    government: '#007AFF',
    competitive: '#5856D6',
    engineering: '#FF9500',
    medical: '#FF3B30',
    scholarship: '#34C759',
    school: '#AF52DE',
    university: '#FF2D92',
    certification: '#5AC8FA',
  };
  
  return colorMap[category] || '#8E8E93';
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 */
export const validatePassword = (password: string): { isValid: boolean; message: string } => {
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters long' };
  }
  
  if (!/(?=.*[a-z])/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one lowercase letter' };
  }
  
  if (!/(?=.*[A-Z])/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one uppercase letter' };
  }
  
  if (!/(?=.*\d)/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one number' };
  }
  
  return { isValid: true, message: 'Password is valid' };
};

/**
 * Get device information
 */
export const getDeviceInfo = () => {
  return {
    platform: Platform.OS,
    version: Platform.Version,
    isIOS: Platform.OS === 'ios',
    isAndroid: Platform.OS === 'android',
  };
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle function
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Generate random ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Check if string is empty or only whitespace
 */
export const isEmpty = (str: string | null | undefined): boolean => {
  return !str || str.trim().length === 0;
};

/**
 * Parse JSON safely
 */
export const parseJSON = <T>(json: string, fallback: T): T => {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Get priority level from score
 */
export const getPriorityLevel = (score: number): 'high' | 'medium' | 'low' => {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
};

/**
 * Get priority color
 */
export const getPriorityColor = (priority: 'high' | 'medium' | 'low'): string => {
  const colorMap = {
    high: '#FF3B30',
    medium: '#FF9500',
    low: '#34C759',
  };
  
  return colorMap[priority];
};
