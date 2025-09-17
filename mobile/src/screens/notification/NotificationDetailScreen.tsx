/**
 * Notification Detail Screen for NoticeWala Mobile App
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Linking,
  Alert,
  Share,
} from 'react-native';
import {
  Text,
  Card,
  Chip,
  Button,
  IconButton,
  Divider,
  ActivityIndicator,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import { markNotificationRead } from '@store/slices/notificationSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';
import {
  formatDate,
  getCategoryColor,
  getCategoryDisplayName,
} from '@utils/helpers';
import { NotificationData } from '@store/slices/notificationSlice';

const NotificationDetailScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Get notification from route params
  const notification = (route.params as any)?.notification as NotificationData;

  useEffect(() => {
    // Mark notification as read when viewing details
    if (notification && !notification.opened_at) {
      dispatch(markNotificationRead(notification.id));
    }
  }, [notification, dispatch]);

  if (!notification) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Notification not found</Text>
          <Text style={styles.errorText}>
            The notification you're looking for could not be found.
          </Text>
          <Button
            mode="contained"
            onPress={() => navigation.goBack()}
            style={styles.errorButton}
          >
            Go Back
          </Button>
        </View>
      </SafeAreaView>
    );
  }

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

  const notificationType = notification.data?.type || 'general';
  const iconName = getNotificationIcon(notificationType);
  const iconColor = getNotificationColor(notificationType);
  const isRead = !!notification.opened_at;

  const handleShare = async () => {
    try {
      await Share.share({
        message: `${notification.title}\n\n${notification.body}\n\nReceived: ${formatDate(notification.created_at)}`,
        title: notification.title,
      });
    } catch (error) {
      Alert.alert('Error', 'Could not share the notification');
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    // TODO: Implement bookmark functionality
  };

  const handleOpenLink = async () => {
    if (notification.data?.link) {
      try {
        await Linking.openURL(notification.data.link);
      } catch (error) {
        Alert.alert('Error', 'Could not open the link');
      }
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header Card */}
        <Card style={[styles.headerCard, !isRead && styles.unreadCard]}>
          <Card.Content>
            <View style={styles.headerTop}>
              <View style={styles.headerLeft}>
                <View style={styles.iconContainer}>
                  <IconButton
                    icon={iconName}
                    size={32}
                    iconColor={iconColor}
                    style={styles.notificationIcon}
                  />
                  {!isRead && <View style={styles.unreadDot} />}
                </View>
                <View style={styles.titleContainer}>
                  <Text style={styles.title} numberOfLines={3}>
                    {notification.title}
                  </Text>
                  <View style={styles.statusContainer}>
                    {isRead ? (
                      <Chip
                        mode="outlined"
                        compact
                        style={styles.readChip}
                        textStyle={styles.readChipText}
                        icon="check"
                      >
                        Read
                      </Chip>
                    ) : (
                      <Chip
                        mode="flat"
                        compact
                        style={styles.unreadChip}
                        textStyle={styles.unreadChipText}
                        icon="circle"
                      >
                        Unread
                      </Chip>
                    )}
                    {notification.data?.priority && (
                      <Chip
                        mode="outlined"
                        compact
                        style={[
                          styles.priorityChip,
                          notification.data.priority === 'high' && styles.highPriorityChip
                        ]}
                        textStyle={[
                          styles.priorityChipText,
                          notification.data.priority === 'high' && styles.highPriorityChipText
                        ]}
                      >
                        {notification.data.priority}
                      </Chip>
                    )}
                  </View>
                </View>
              </View>
              
              <View style={styles.headerActions}>
                <IconButton
                  icon={isBookmarked ? 'bookmark' : 'bookmark-outline'}
                  onPress={handleBookmark}
                  iconColor={isBookmarked ? colors.primary : colors.textSecondary}
                />
                <IconButton
                  icon="share"
                  onPress={handleShare}
                  iconColor={colors.textSecondary}
                />
              </View>
            </View>

            <Text style={styles.body}>
              {notification.body}
            </Text>

            <View style={styles.metaInfo}>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Type:</Text>
                <Chip
                  mode="outlined"
                  compact
                  style={[styles.typeChip, { borderColor: iconColor }]}
                  textStyle={[styles.typeChipText, { color: iconColor }]}
                >
                  {notificationType.replace('_', ' ').toUpperCase()}
                </Chip>
              </View>
              
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Received:</Text>
                <Text style={styles.metaValue}>
                  {formatDate(notification.created_at)}
                </Text>
              </View>
              
              {notification.opened_at && (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Read:</Text>
                  <Text style={styles.metaValue}>
                    {formatDate(notification.opened_at)}
                  </Text>
                </View>
              )}
            </View>
          </Card.Content>
        </Card>

        {/* Notification Data */}
        {notification.data && Object.keys(notification.data).length > 0 && (
          <Card style={styles.dataCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Additional Information</Text>
              
              {notification.data.exam_date && (
                <View style={styles.dataItem}>
                  <Text style={styles.dataLabel}>Exam Date:</Text>
                  <Text style={styles.dataValue}>
                    {formatDate(notification.data.exam_date)}
                  </Text>
                </View>
              )}
              
              {notification.data.deadline && (
                <View style={styles.dataItem}>
                  <Text style={styles.dataLabel}>Deadline:</Text>
                  <Text style={styles.dataValue}>
                    {formatDate(notification.data.deadline)}
                  </Text>
                </View>
              )}
              
              {notification.data.source && (
                <View style={styles.dataItem}>
                  <Text style={styles.dataLabel}>Source:</Text>
                  <Text style={styles.dataValue}>
                    {notification.data.source}
                  </Text>
                </View>
              )}
              
              {notification.data.categories && notification.data.categories.length > 0 && (
                <View style={styles.categoriesContainer}>
                  <Text style={styles.dataLabel}>Categories:</Text>
                  <View style={styles.categoriesList}>
                    {notification.data.categories.map((category) => (
                      <Chip
                        key={category}
                        mode="outlined"
                        style={[
                          styles.categoryChip,
                          { borderColor: getCategoryColor(category) }
                        ]}
                        textStyle={[
                          styles.categoryChipText,
                          { color: getCategoryColor(category) }
                        ]}
                      >
                        {getCategoryDisplayName(category)}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}
            </Card.Content>
          </Card>
        )}

        {/* Actions */}
        <Card style={styles.actionsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Actions</Text>
            
            {notification.data?.link && (
              <Button
                mode="contained"
                onPress={handleOpenLink}
                icon="open-in-new"
                style={styles.actionButton}
              >
                Open Link
              </Button>
            )}
            
            <Button
              mode="outlined"
              onPress={handleShare}
              icon="share"
              style={styles.actionButton}
            >
              Share Notification
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: spacing.md,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  errorTitle: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  errorText: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  errorButton: {
    borderRadius: borderRadius.md,
  },
  headerCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  unreadCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
    backgroundColor: colors.primary + '05',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  headerLeft: {
    flex: 1,
    flexDirection: 'row',
    marginRight: spacing.sm,
  },
  iconContainer: {
    position: 'relative',
    marginRight: spacing.sm,
  },
  notificationIcon: {
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
  titleContainer: {
    flex: 1,
  },
  title: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  readChip: {
    backgroundColor: colors.success + '20',
    borderColor: colors.success,
    marginRight: spacing.sm,
  },
  readChipText: {
    color: colors.success,
    fontSize: 12,
  },
  unreadChip: {
    backgroundColor: colors.primary,
    marginRight: spacing.sm,
  },
  unreadChipText: {
    color: colors.surface,
    fontSize: 12,
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
  headerActions: {
    flexDirection: 'row',
  },
  body: {
    ...typography.body1,
    color: colors.text,
    lineHeight: 24,
    marginBottom: spacing.md,
  },
  metaInfo: {
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: borderRadius.md,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  metaLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    minWidth: 80,
  },
  metaValue: {
    ...typography.body2,
    color: colors.text,
    flex: 1,
  },
  typeChip: {
    height: 24,
  },
  typeChipText: {
    fontSize: 10,
  },
  dataCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  sectionTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.md,
  },
  dataItem: {
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
  },
  dataLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    fontWeight: '500',
    marginBottom: spacing.xs,
  },
  dataValue: {
    ...typography.body1,
    color: colors.text,
  },
  categoriesContainer: {
    marginTop: spacing.sm,
  },
  categoriesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: spacing.sm,
  },
  categoryChip: {
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  },
  categoryChipText: {
    fontSize: 12,
  },
  actionsCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  actionButton: {
    marginBottom: spacing.sm,
    borderRadius: borderRadius.md,
  },
});

export default NotificationDetailScreen;
