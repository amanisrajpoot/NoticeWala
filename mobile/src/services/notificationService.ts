/**
 * Push Notification Service for NoticeWala Mobile App
 * Handles FCM integration and local notifications
 */

import { Platform, Alert } from 'react-native';
import PushNotification from 'react-native-push-notification';
import messaging from '@react-native-firebase/messaging';
import { apiService, endpoints } from './apiService';
import DeviceInfo from 'react-native-device-info';

// Types
export interface PushTokenData {
  token: string;
  platform: 'ios' | 'android' | 'web';
  device_id?: string;
  app_version?: string;
  os_version?: string;
}

export interface NotificationData {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  status: string;
  created_at: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
}

export interface NotificationSettings {
  push_enabled: boolean;
  email_enabled: boolean;
  quiet_hours?: {
    enabled: boolean;
    start_time: string;
    end_time: string;
    timezone: string;
  };
  priority_threshold: number;
  categories?: string[];
  sources?: string[];
}

class NotificationService {
  private isInitialized = false;
  private fcmToken: string | null = null;

  /**
   * Initialize push notifications
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      // Configure local notifications
      this.configureLocalNotifications();

      // Request permission and get FCM token
      await this.requestPermission();
      const token = await this.getFCMToken();
      
      if (token) {
        await this.registerPushToken(token);
      }

      // Set up message handlers
      this.setupMessageHandlers();

      this.isInitialized = true;
      console.log('Notification service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize notification service:', error);
    }
  }

  /**
   * Configure local notifications
   */
  private configureLocalNotifications(): void {
    PushNotification.configure({
      onRegister: (token) => {
        console.log('Local notification token:', token);
      },

      onNotification: (notification) => {
        console.log('Local notification received:', notification);
        this.handleLocalNotification(notification);
      },

      onAction: (notification) => {
        console.log('Local notification action:', notification);
      },

      onRegistrationError: (err) => {
        console.error('Local notification registration error:', err);
      },

      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },

      popInitialNotification: true,
      requestPermissions: Platform.OS === 'ios',
    });

    // Create default channel for Android
    if (Platform.OS === 'android') {
      PushNotification.createChannel(
        {
          channelId: 'noticewala-default',
          channelName: 'NoticeWala Notifications',
          channelDescription: 'Default notification channel for NoticeWala',
          playSound: true,
          soundName: 'default',
          importance: 4,
          vibrate: true,
        },
        (created) => console.log(`Channel created: ${created}`)
      );
    }
  }

  /**
   * Request notification permission
   */
  private async requestPermission(): Promise<boolean> {
    try {
      if (Platform.OS === 'ios') {
        const authStatus = await messaging().requestPermission();
        const enabled =
          authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
          authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        if (!enabled) {
          Alert.alert(
            'Permission Required',
            'Please enable notifications in Settings to receive exam updates.',
            [{ text: 'OK' }]
          );
        }

        return enabled;
      } else {
        // Android permissions are handled automatically
        return true;
      }
    } catch (error) {
      console.error('Permission request error:', error);
      return false;
    }
  }

  /**
   * Get FCM token
   */
  private async getFCMToken(): Promise<string | null> {
    try {
      const token = await messaging().getToken();
      this.fcmToken = token;
      console.log('FCM Token:', token);
      return token;
    } catch (error) {
      console.error('Get FCM token error:', error);
      return null;
    }
  }

  /**
   * Register push token with backend
   */
  private async registerPushToken(fcmToken: string): Promise<void> {
    try {
      const deviceInfo = await this.getDeviceInfo();
      
      const tokenData: PushTokenData = {
        token: fcmToken,
        platform: Platform.OS as 'ios' | 'android',
        device_id: deviceInfo.deviceId,
        app_version: deviceInfo.appVersion,
        os_version: deviceInfo.osVersion,
      };

      await apiService.post(endpoints.users.pushToken, tokenData);
      console.log('Push token registered successfully');
    } catch (error) {
      console.error('Register push token error:', error);
    }
  }

  /**
   * Get device information
   */
  private async getDeviceInfo() {
    try {
      const [deviceId, appVersion, osVersion] = await Promise.all([
        DeviceInfo.getUniqueId(),
        DeviceInfo.getVersion(),
        DeviceInfo.getSystemVersion(),
      ]);

      return {
        deviceId,
        appVersion,
        osVersion,
      };
    } catch (error) {
      console.error('Get device info error:', error);
      return {
        deviceId: 'unknown',
        appVersion: '1.0.0',
        osVersion: 'unknown',
      };
    }
  }

  /**
   * Set up message handlers
   */
  private setupMessageHandlers(): void {
    // Handle foreground messages
    messaging().onMessage(async (remoteMessage) => {
      console.log('Foreground message received:', remoteMessage);
      
      // Show local notification for foreground messages
      this.showLocalNotification({
        title: remoteMessage.notification?.title || 'NoticeWala',
        body: remoteMessage.notification?.body || '',
        data: remoteMessage.data,
      });
    });

    // Handle background messages
    messaging().setBackgroundMessageHandler(async (remoteMessage) => {
      console.log('Background message received:', remoteMessage);
    });

    // Handle notification opened app
    messaging().onNotificationOpenedApp((remoteMessage) => {
      console.log('Notification opened app:', remoteMessage);
      this.handleNotificationOpen(remoteMessage);
    });

    // Handle notification when app is closed
    messaging()
      .getInitialNotification()
      .then((remoteMessage) => {
        if (remoteMessage) {
          console.log('App opened from notification:', remoteMessage);
          this.handleNotificationOpen(remoteMessage);
        }
      });
  }

  /**
   * Show local notification
   */
  showLocalNotification(notification: {
    title: string;
    body: string;
    data?: Record<string, any>;
  }): void {
    PushNotification.localNotification({
      channelId: 'noticewala-default',
      title: notification.title,
      message: notification.body,
      playSound: true,
      soundName: 'default',
      userInfo: notification.data,
    });
  }

  /**
   * Handle local notification
   */
  private handleLocalNotification(notification: any): void {
    console.log('Local notification handled:', notification);
    // Handle notification tap, etc.
  }

  /**
   * Handle notification open
   */
  private handleNotificationOpen(remoteMessage: any): void {
    console.log('Notification open handled:', remoteMessage);
    // Navigate to relevant screen based on notification data
    // This would typically use navigation service
  }

  /**
   * Get user notifications from backend
   */
  async getUserNotifications(skip = 0, limit = 20): Promise<{
    items: NotificationData[];
    total: number;
  }> {
    try {
      const response = await apiService.get<{
        items: NotificationData[];
        total: number;
      }>(`${endpoints.notifications.list}?skip=${skip}&limit=${limit}`);
      
      return response;
    } catch (error) {
      console.error('Get user notifications error:', error);
      throw error;
    }
  }

  /**
   * Mark notification as read
   */
  async markNotificationRead(notificationId: string): Promise<void> {
    try {
      await apiService.put(endpoints.notifications.read(notificationId));
    } catch (error) {
      console.error('Mark notification read error:', error);
      throw error;
    }
  }

  /**
   * Delete notification
   */
  async deleteNotification(notificationId: string): Promise<void> {
    try {
      await apiService.delete(endpoints.notifications.delete(notificationId));
    } catch (error) {
      console.error('Delete notification error:', error);
      throw error;
    }
  }

  /**
   * Get notification settings
   */
  async getNotificationSettings(): Promise<NotificationSettings> {
    try {
      const response = await apiService.get<NotificationSettings>(endpoints.notifications.settings);
      return response;
    } catch (error) {
      console.error('Get notification settings error:', error);
      throw error;
    }
  }

  /**
   * Unregister push token
   */
  async unregisterPushToken(token: string): Promise<void> {
    try {
      await apiService.delete(endpoints.users.deletePushToken(token));
      console.log('Push token unregistered successfully');
    } catch (error) {
      console.error('Unregister push token error:', error);
      throw error;
    }
  }

  /**
   * Clear all notifications
   */
  clearAllNotifications(): void {
    PushNotification.cancelAllLocalNotifications();
  }

  /**
   * Set badge count (iOS)
   */
  setBadgeCount(count: number): void {
    if (Platform.OS === 'ios') {
      PushNotification.setApplicationIconBadgeNumber(count);
    }
  }
}

// Create singleton instance
export const notificationService = new NotificationService();

// Initialize function for app startup
export const initializePushNotifications = async (): Promise<void> => {
  await notificationService.initialize();
};

export default notificationService;
