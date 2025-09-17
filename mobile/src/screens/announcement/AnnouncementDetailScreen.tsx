/**
 * Announcement Detail Screen for NoticeWala Mobile App
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
import { fetchAnnouncementById } from '@store/slices/announcementSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';
import {
  formatDate,
  getTimeUntilDeadline,
  isDeadlineUrgent,
  getCategoryColor,
  getCategoryDisplayName,
} from '@utils/helpers';
import { Announcement } from '@store/slices/announcementSlice';

const AnnouncementDetailScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  
  const { currentAnnouncement, isLoading } = useAppSelector((state) => state.announcements);
  
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Get announcement ID from route params
  const announcementId = (route.params as any)?.announcementId;
  const announcementFromParams = (route.params as any)?.announcement;

  useEffect(() => {
    if (announcementId && !currentAnnouncement && !announcementFromParams) {
      dispatch(fetchAnnouncementById(announcementId));
    }
  }, [announcementId, currentAnnouncement, announcementFromParams, dispatch]);

  const handleOpenSource = async () => {
    if (announcement?.source_url) {
      try {
        await Linking.openURL(announcement.source_url);
      } catch (error) {
        Alert.alert('Error', 'Could not open the source URL');
      }
    }
  };

  const handleShare = async () => {
    if (announcement) {
      try {
        await Share.share({
          message: `${announcement.title}\n\n${announcement.summary || announcement.content || ''}\n\nSource: ${announcement.source_url}`,
          title: announcement.title,
        });
      } catch (error) {
        Alert.alert('Error', 'Could not share the announcement');
      }
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    // TODO: Implement bookmark functionality
  };

  const handleCreateSubscription = () => {
    // TODO: Navigate to create subscription with pre-filled data
    Alert.alert('Create Subscription', 'This will create a subscription for similar announcements.');
  };

  if (isLoading && !announcementFromParams) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Loading announcement...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!announcement) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Announcement not found</Text>
          <Text style={styles.errorText}>
            The announcement you're looking for could not be found.
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

  const announcement = announcementFromParams || currentAnnouncement;
  const isUrgent = announcement.application_deadline 
    ? isDeadlineUrgent(announcement.application_deadline)
    : false;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header Card */}
        <Card style={[styles.headerCard, isUrgent && styles.urgentCard]}>
          <Card.Content>
            <View style={styles.headerTop}>
              <View style={styles.headerLeft}>
                <Text style={styles.title} numberOfLines={3}>
                  {announcement.title}
                </Text>
                {announcement.is_verified && (
                  <Chip
                    mode="outlined"
                    compact
                    style={styles.verifiedChip}
                    textStyle={styles.verifiedChipText}
                    icon="check"
                  >
                    Verified
                  </Chip>
                )}
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

            {announcement.summary && (
              <Text style={styles.summary}>
                {announcement.summary}
              </Text>
            )}

            <View style={styles.metaInfo}>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Source:</Text>
                <Text style={styles.metaValue}>{announcement.source.name}</Text>
              </View>
              
              {announcement.publish_date && (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Published:</Text>
                  <Text style={styles.metaValue}>
                    {formatDate(announcement.publish_date)}
                  </Text>
                </View>
              )}
              
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Priority:</Text>
                <Chip
                  mode="outlined"
                  compact
                  style={[
                    styles.priorityChip,
                    { borderColor: getCategoryColor(announcement.categories?.[0] || 'other') }
                  ]}
                  textStyle={[
                    styles.priorityChipText,
                    { color: getCategoryColor(announcement.categories?.[0] || 'other') }
                  ]}
                >
                  {Math.round(announcement.priority_score * 100)}%
                </Chip>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Categories */}
        {announcement.categories && announcement.categories.length > 0 && (
          <Card style={styles.categoriesCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Categories</Text>
              <View style={styles.categoriesContainer}>
                {announcement.categories.map((category) => (
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
            </Card.Content>
          </Card>
        )}

        {/* Important Dates */}
        {(announcement.exam_dates || announcement.application_deadline) && (
          <Card style={styles.datesCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Important Dates</Text>
              
              {announcement.application_deadline && (
                <View style={[styles.dateItem, isUrgent && styles.urgentDateItem]}>
                  <View style={styles.dateHeader}>
                    <Text style={styles.dateLabel}>Application Deadline</Text>
                    {isUrgent && (
                      <Chip
                        mode="flat"
                        compact
                        style={styles.urgentChip}
                        textStyle={styles.urgentChipText}
                      >
                        Urgent
                      </Chip>
                    )}
                  </View>
                  <Text style={[styles.dateValue, isUrgent && styles.urgentDateValue]}>
                    {formatDate(announcement.application_deadline)}
                  </Text>
                  <Text style={[styles.dateNote, isUrgent && styles.urgentDateNote]}>
                    {getTimeUntilDeadline(announcement.application_deadline)} left
                  </Text>
                </View>
              )}

              {announcement.exam_dates && announcement.exam_dates.map((examDate, index) => (
                <View key={index} style={styles.dateItem}>
                  <Text style={styles.dateLabel}>
                    {examDate.type === 'exam_date' ? 'Exam Date' : 
                     examDate.type === 'result_date' ? 'Result Date' : 
                     examDate.note || examDate.type}
                  </Text>
                  <Text style={styles.dateValue}>
                    {formatDate(examDate.start)}
                    {examDate.end && examDate.end !== examDate.start && 
                      ` - ${formatDate(examDate.end)}`
                    }
                  </Text>
                </View>
              ))}
            </Card.Content>
          </Card>
        )}

        {/* Eligibility */}
        {announcement.eligibility && (
          <Card style={styles.eligibilityCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Eligibility</Text>
              <Text style={styles.eligibilityText}>
                {announcement.eligibility}
              </Text>
            </Card.Content>
          </Card>
        )}

        {/* Content */}
        {announcement.content && (
          <Card style={styles.contentCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Details</Text>
              <Text style={styles.contentText}>
                {announcement.content}
              </Text>
            </Card.Content>
          </Card>
        )}

        {/* Attachments */}
        {announcement.attachments && announcement.attachments.length > 0 && (
          <Card style={styles.attachmentsCard}>
            <Card.Content>
              <Text style={styles.sectionTitle}>Attachments</Text>
              {announcement.attachments.map((attachment) => (
                <Button
                  key={attachment.id}
                  mode="outlined"
                  icon="file-document"
                  onPress={() => Linking.openURL(attachment.file_url)}
                  style={styles.attachmentButton}
                >
                  {attachment.title || attachment.filename}
                </Button>
              ))}
            </Card.Content>
          </Card>
        )}

        {/* Actions */}
        <Card style={styles.actionsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Actions</Text>
            
            <Button
              mode="contained"
              onPress={handleOpenSource}
              icon="open-in-new"
              style={styles.actionButton}
            >
              View Original Source
            </Button>
            
            <Button
              mode="outlined"
              onPress={handleCreateSubscription}
              icon="bell-plus"
              style={styles.actionButton}
            >
              Subscribe to Similar
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    ...typography.body1,
    color: colors.textSecondary,
    marginTop: spacing.md,
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
  urgentCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  headerLeft: {
    flex: 1,
    marginRight: spacing.sm,
  },
  title: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  verifiedChip: {
    backgroundColor: colors.success + '20',
    borderColor: colors.success,
  },
  verifiedChipText: {
    color: colors.success,
    fontSize: 12,
  },
  headerActions: {
    flexDirection: 'row',
  },
  summary: {
    ...typography.body1,
    color: colors.textSecondary,
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
  priorityChip: {
    height: 24,
  },
  priorityChipText: {
    fontSize: 12,
  },
  categoriesCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  sectionTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.md,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  categoryChip: {
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  },
  categoryChipText: {
    fontSize: 12,
  },
  datesCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  dateItem: {
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
  },
  urgentDateItem: {
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
    backgroundColor: colors.error + '05',
  },
  dateHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  dateLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  urgentChip: {
    backgroundColor: colors.error,
  },
  urgentChipText: {
    color: colors.surface,
    fontSize: 10,
  },
  dateValue: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  urgentDateValue: {
    color: colors.error,
  },
  dateNote: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  urgentDateNote: {
    color: colors.error,
  },
  eligibilityCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  eligibilityText: {
    ...typography.body1,
    color: colors.text,
    lineHeight: 24,
  },
  contentCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  contentText: {
    ...typography.body1,
    color: colors.text,
    lineHeight: 24,
  },
  attachmentsCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.lg,
  },
  attachmentButton: {
    marginBottom: spacing.sm,
    borderRadius: borderRadius.md,
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

export default AnnouncementDetailScreen;
