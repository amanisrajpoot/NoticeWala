/**
 * Theme configuration for NoticeWala Mobile App
 */

import { DefaultTheme } from 'react-native-paper';

// Colors
export const colors = {
  primary: '#007AFF',
  primaryDark: '#0056CC',
  secondary: '#5856D6',
  accent: '#FF3B30',
  background: '#F2F2F7',
  surface: '#FFFFFF',
  text: '#000000',
  textSecondary: '#8E8E93',
  textLight: '#C7C7CC',
  border: '#E5E5EA',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  info: '#007AFF',
  
  // Status colors
  verified: '#34C759',
  pending: '#FF9500',
  expired: '#FF3B30',
  
  // Category colors
  government: '#007AFF',
  competitive: '#5856D6',
  engineering: '#FF9500',
  medical: '#FF3B30',
  scholarship: '#34C759',
  school: '#AF52DE',
  university: '#FF2D92',
  
  // Priority colors
  high: '#FF3B30',
  medium: '#FF9500',
  low: '#34C759',
};

// Paper theme
export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    accent: colors.accent,
    background: colors.background,
    surface: colors.surface,
    text: colors.text,
    placeholder: colors.textSecondary,
    disabled: colors.textLight,
    error: colors.error,
    notification: colors.accent,
  },
  roundness: 12,
  fonts: {
    ...DefaultTheme.fonts,
    regular: {
      fontFamily: 'System',
      fontWeight: '400' as const,
    },
    medium: {
      fontFamily: 'System',
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: 'System',
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: 'System',
      fontWeight: '100' as const,
    },
  },
};

// Typography
export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: '700',
    lineHeight: 40,
  },
  h2: {
    fontSize: 28,
    fontWeight: '600',
    lineHeight: 36,
  },
  h3: {
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
  },
  h4: {
    fontSize: 20,
    fontWeight: '500',
    lineHeight: 28,
  },
  h5: {
    fontSize: 18,
    fontWeight: '500',
    lineHeight: 24,
  },
  h6: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 22,
  },
  body1: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 16,
  },
  overline: {
    fontSize: 10,
    fontWeight: '500',
    lineHeight: 16,
    textTransform: 'uppercase',
  },
};

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Border radius
export const borderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  round: 50,
};

// Shadows
export const shadows = {
  small: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  large: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
};

// Animation durations
export const animations = {
  fast: 200,
  normal: 300,
  slow: 500,
};

// Breakpoints (for responsive design)
export const breakpoints = {
  small: 320,
  medium: 768,
  large: 1024,
};

export default theme;
