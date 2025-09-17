/**
 * Notifications Screen for NoticeWala Mobile App
 */

import React, { useEffect, useCallback, useState } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import {
  Text,
  Card,
  Button,
  Chip,
  Menu,
  IconButton,
  Badge,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import {
  fetchNotifications,
  markNotificationRead,
  deleteNotification,
  fetchNotificationSettings,
} from '@store/slices/notificationSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';
import { formatDate } from '@utils/helpers';
import { NotificationData } from '@store/slices/notificationSlice';

const NotificationsScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  
  const {
    notifications,
    unreadCount,
    settings,
    isLoading,
    isRefreshing,
    hasMore,
    totalCount,
  } = useAppSelector((state) => state.notifications);
  
  const [filterStatus, setFilterStatus] = useState<string | undefined>();
  const [menuVisible, setMenuVisible] = useState(false);

  const statusOptions = [
    { label: 'All', value: undefined },
    { label: 'Unread', value: 'unread' },
    { label: 'Read', value: 'read' },
  ];

  // Load notifications on mount
  useEffect(() => {
    loadNotifications();
    dispatch(fetchNotificationSettings());
  }, []);

  const loadNotifications = useCallback(async () => {
    await dispatch(fetchNotifications({
      skip: 0,
      limit: 20,
      status: filterStatus,
    }));
  }, [dispatch, filterStatus]);

  const loadMoreNotifications = useCallback(async () => {
    if (!hasMore || isLoading) return;
    
    await dispatch(fetchNotifications({
      skip: notifications.length,
      limit: 20,
      status: filterStatus,
    }));
  }, [hasMore, isLoading, notifications.length, filterStatus, dispatch]);

  const handleRefresh = useCallback(async () => {
    await loadNotifications();
  }, [loadNotifications]);

  const handleMarkAsRead = useCallback(async (notificationId: string) => {
    try {
      await dispatch(markNotificationRead(notificationId));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }, [dispatch]);

  const handleDeleteNotification = useCallback(async (notificationId: string) => {
    try {
      await dispatch(deleteNotification(notificationId));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  }, [dispatch]);

  const handleFilterChange = useCallback((status: string | undefined) => {
    setFilterStatus(status);
    setMenuVisible(false);
  }, []);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'exam_notification':
        return 'school';
      case 'deadline_reminder':
        return 'alarm';
      case 'system':
        return 'information';
      default:
        return 'bell';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'exam_notification':
        return colors.primary;
      case 'deadline_reminder':
        return colors.error;
      case 'system':
        return colors.info;
      default:
        return colors.textSecondary;
    }
  };

  const renderNotificationItem = ({ item }: { item: NotificationData }) => {
    const isRead = !!item.opened_at;
    const notificationType = item.data?.type || 'general';
    const iconName = getNotificationIcon(notificationType);
    const iconColor = getNotificationColor(notificationType);

    return (
      <Card 
        style={[
          styles.notificationCard,
          !isRead && styles.unreadNotification
        ]}
      >
        <Card.Content style={styles.notificationContent}>
          <View style={styles.notificationHeader}>
            <View style={styles.notificationIcon}>
              <IconButton
                icon={iconName}
                size={24}
                iconColor={iconColor}
                style={styles.iconButton}
              />
              {!isRead && <View style={styles.unreadDot} />}
            </View>
            
            <View style={styles.notificationText}>
              <Text style={styles.notificationTitle} numberOfLines={2}>
                {item.title}
              </Text>
              <Text style={styles.notificationBody} numberOfLines={3}>
                {item.body}
              </Text>
            </View>
            
            <View style={styles.notificationActions}>
              <Menu
                visible={menuVisible}
                onDismiss={() => setMenuVisible(false)}
                anchor={
                  <IconButton
                    icon="dots-vertical"
                    size={20}
                    onPress={() => setMenuVisible(true)}
                  />
                }
              >
                {!isRead && (
                  <Menu.Item
                    onPress={() => handleMarkAsRead(item.id)}
                    title="Mark as Read"
                    leadingIcon="check"
                  />
                )}
                <Menu.Item
                  onPress={() => handleDeleteNotification(item.id)}
                  title="Delete"
                  leadingIcon="delete"
                  titleStyle={{ color: colors.error }}
                />
              </Menu>
            </View>
          </View>
          
          <View style={styles.notificationFooter}>
            <Text style={styles.notificationDate}>
              {formatDate(item.created_at, 'relative')}
            </Text>
            
            {item.data?.priority && (
              <Chip
                mode="outlined"
                compact
                style={[
                  styles.priorityChip,
                  item.data.priority === 'high' && styles.highPriorityChip
                ]}
                textStyle={[
                  styles.priorityChipText,
                  item.data.priority === 'high' && styles.highPriorityChipText
                ]}
              >
                {item.data.priority}
              </Chip>
            )}
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerTop}>
        <Text style={styles.headerTitle}>Notifications</Text>
        <View style={styles.headerActions}>
          <Menu
            visible={menuVisible}
            onDismiss={() => setMenuVisible(false)}
            anchor={
              <Button
                mode="outlined"
                onPress={() => setMenuVisible(true)}
                icon="filter"
                compact
              >
                Filter
              </Button>
            }
          >
            {statusOptions.map((option) => (
              <Menu.Item
                key={option.value || 'all'}
                onPress={() => handleFilterChange(option.value)}
                title={option.label}
                titleStyle={filterStatus === option.value ? { color: colors.primary } : {}}
              />
            ))}
          </Menu>
        </View>
      </View>
      
      {settings && (
        <View style={styles.settingsInfo}>
          <Text style={styles.settingsText}>
            Push notifications: {settings.push_enabled ? 'Enabled' : 'Disabled'}
          </Text>
          {unreadCount > 0 && (
            <Badge style={styles.unreadBadge}>{unreadCount}</Badge>
          )}
        </View>
      )}
      
      <View style={styles.statsContainer}>
        <Text style={styles.statsText}>
          {totalCount} total notifications
        </Text>
      </View>
    </View>
  );

  const renderFooter = () => {
    if (!isLoading || notifications.length === 0) return null;
    
    return (
      <View style={styles.loadingFooter}>
        <ActivityIndicator size="small" color={colors.primary} />
      </View>
    );
  };

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyTitle}>No notifications</Text>
      <Text style={styles.emptySubtitle}>
        You'll see exam notifications and reminders here
      </Text>
      <Button
        mode="outlined"
        onPress={handleRefresh}
        style={styles.emptyButton}
      >
        Refresh
      </Button>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={notifications}
        renderItem={renderNotificationItem}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
        onEndReached={loadMoreNotifications}
        onEndReachedThreshold={0.1}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    padding: spacing.md,
  },
  header: {
    marginBottom: spacing.lg,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  headerTitle: {
    ...typography.h4,
    color: colors.text,
  },
  headerActions: {
    flexDirection: 'row',
  },
  settingsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  settingsText: {
    ...typography.body2,
    color: colors.textSecondary,
    flex: 1,
  },
  unreadBadge: {
    backgroundColor: colors.primary,
  },
  statsContainer: {
    alignItems: 'center',
  },
  statsText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  notificationCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.md,
  },
  unreadNotification: {
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
    backgroundColor: colors.primary + '05',
  },
  notificationContent: {
    padding: spacing.md,
  },
  notificationHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  notificationIcon: {
    position: 'relative',
    marginRight: spacing.sm,
  },
  iconButton: {
    margin: 0,
  },
  unreadDot: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
  notificationText: {
    flex: 1,
    marginRight: spacing.sm,
  },
  notificationTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  notificationBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  notificationActions: {
    alignItems: 'center',
  },
  notificationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  notificationDate: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  priorityChip: {
    height: 24,
  },
  priorityChipText: {
    fontSize: 10,
  },
  highPriorityChip: {
    backgroundColor: colors.error + '20',
    borderColor: colors.error,
  },
  highPriorityChipText: {
    color: colors.error,
  },
  loadingFooter: {
    padding: spacing.lg,
    alignItems: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xxl,
  },
  emptyTitle: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  emptySubtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  emptyButton: {
    borderRadius: borderRadius.md,
  },
});

export default NotificationsScreen;
