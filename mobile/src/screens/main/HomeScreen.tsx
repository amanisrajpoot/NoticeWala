/**
 * Home Screen for NoticeWala Mobile App
 */

import React, { useEffect, useState, useCallback } from 'react';
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
  Chip,
  Button,
  Searchbar,
  FAB,
  Badge,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import {
  fetchAnnouncements,
  fetchCategories,
  setFilters,
  clearAnnouncements,
} from '@store/slices/announcementSlice';
import {
  fetchNotifications,
  selectUnreadCount,
} from '@store/slices/notificationSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';
import {
  formatDate,
  getTimeUntilDeadline,
  isDeadlineUrgent,
  getCategoryColor,
  getCategoryDisplayName,
  truncateText,
} from '@utils/helpers';
import { Announcement } from '@store/slices/announcementSlice';

const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  
  const {
    announcements,
    categories,
    filters,
    isLoading,
    isRefreshing,
    hasMore,
    totalCount,
    error,
  } = useAppSelector((state) => state.announcements);
  
  const unreadCount = useAppSelector(selectUnreadCount);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    dispatch(fetchCategories());
    dispatch(fetchNotifications({ skip: 0, limit: 10 }));
    loadAnnouncements();
  }, []);

  const loadAnnouncements = useCallback(async () => {
    const newFilters = {
      ...filters,
      search: searchQuery || undefined,
      category: selectedCategory || undefined,
      skip: 0,
    };
    
    dispatch(setFilters(newFilters));
    await dispatch(fetchAnnouncements(newFilters));
  }, [searchQuery, selectedCategory, filters, dispatch]);

  const loadMoreAnnouncements = useCallback(async () => {
    if (!hasMore || isLoading) return;
    
    const newFilters = {
      ...filters,
      skip: announcements.length,
    };
    
    await dispatch(fetchAnnouncements(newFilters));
  }, [hasMore, isLoading, filters, announcements.length, dispatch]);

  const handleRefresh = useCallback(async () => {
    dispatch(clearAnnouncements());
    await loadAnnouncements();
  }, [dispatch, loadAnnouncements]);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    // Debounce search
    setTimeout(() => {
      if (query === searchQuery) {
        loadAnnouncements();
      }
    }, 500);
  }, [searchQuery, loadAnnouncements]);

  const handleCategorySelect = useCallback((category: string | null) => {
    setSelectedCategory(category);
    loadAnnouncements();
  }, [loadAnnouncements]);

  const handleAnnouncementPress = useCallback((announcement: Announcement) => {
    navigation.navigate('AnnouncementDetail' as never, { announcement } as never);
  }, [navigation]);

  const handleNotificationsPress = useCallback(() => {
    navigation.navigate('Notifications' as never);
  }, [navigation]);

  const handleSearchPress = useCallback(() => {
    navigation.navigate('Search' as never);
  }, [navigation]);

  const handleSubscriptionPress = useCallback(() => {
    navigation.navigate('Subscription' as never);
  }, [navigation]);

  const renderAnnouncementItem = ({ item }: { item: Announcement }) => {
    const isUrgent = item.application_deadline 
      ? isDeadlineUrgent(item.application_deadline)
      : false;

    return (
      <Card 
        style={[styles.announcementCard, isUrgent && styles.urgentCard]}
        onPress={() => handleAnnouncementPress(item)}
      >
        <Card.Content>
          <View style={styles.announcementHeader}>
            <Text style={styles.announcementTitle} numberOfLines={2}>
              {item.title}
            </Text>
            {item.is_verified && (
              <Chip
                mode="outlined"
                compact
                style={styles.verifiedChip}
                textStyle={styles.verifiedChipText}
              >
                Verified
              </Chip>
            )}
          </View>

          {item.summary && (
            <Text style={styles.announcementSummary} numberOfLines={3}>
              {item.summary}
            </Text>
          )}

          <View style={styles.announcementMeta}>
            <Text style={styles.sourceName}>{item.source.name}</Text>
            <Text style={styles.publishDate}>
              {formatDate(item.publish_date || item.created_at, 'relative')}
            </Text>
          </View>

          {item.categories && item.categories.length > 0 && (
            <View style={styles.categoriesContainer}>
              {item.categories.slice(0, 3).map((category) => (
                <Chip
                  key={category}
                  mode="outlined"
                  compact
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
          )}

          {item.application_deadline && (
            <View style={styles.deadlineContainer}>
              <Text style={styles.deadlineLabel}>Application Deadline:</Text>
              <Text 
                style={[
                  styles.deadlineText,
                  isUrgent && styles.urgentDeadlineText
                ]}
              >
                {formatDate(item.application_deadline)} 
                ({getTimeUntilDeadline(item.application_deadline)} left)
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderCategoryChip = ({ item }: { item: string }) => (
    <Chip
      mode={selectedCategory === item ? 'flat' : 'outlined'}
      selected={selectedCategory === item}
      onPress={() => handleCategorySelect(selectedCategory === item ? null : item)}
      style={[
        styles.filterChip,
        selectedCategory === item && { backgroundColor: getCategoryColor(item) }
      ]}
      textStyle={[
        styles.filterChipText,
        selectedCategory === item && { color: colors.surface }
      ]}
    >
      {getCategoryDisplayName(item)}
    </Chip>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="Search announcements..."
          onChangeText={handleSearch}
          value={searchQuery}
          style={styles.searchbar}
          onIconPress={handleSearchPress}
        />
        <Button
          mode="outlined"
          icon="bell"
          onPress={handleNotificationsPress}
          style={styles.notificationButton}
          contentStyle={styles.notificationButtonContent}
        >
          {unreadCount > 0 && (
            <Badge style={styles.notificationBadge}>{unreadCount}</Badge>
          )}
        </Button>
      </View>

      {categories.length > 0 && (
        <View style={styles.categoriesSection}>
          <Text style={styles.sectionTitle}>Categories</Text>
          <FlatList
            data={categories}
            renderItem={renderCategoryChip}
            keyExtractor={(item) => item}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoriesList}
          />
        </View>
      )}

      <View style={styles.statsContainer}>
        <Text style={styles.statsText}>
          {totalCount} announcements found
        </Text>
      </View>
    </View>
  );

  const renderFooter = () => {
    if (!isLoading || announcements.length === 0) return null;
    
    return (
      <View style={styles.loadingFooter}>
        <ActivityIndicator size="small" color={colors.primary} />
      </View>
    );
  };

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyTitle}>No announcements found</Text>
      <Text style={styles.emptySubtitle}>
        Try adjusting your search or filters
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
        data={announcements}
        renderItem={renderAnnouncementItem}
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
        onEndReached={loadMoreAnnouncements}
        onEndReachedThreshold={0.1}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={handleSubscriptionPress}
        label="New Subscription"
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
    paddingBottom: 100, // Space for FAB
  },
  header: {
    marginBottom: spacing.lg,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  searchbar: {
    flex: 1,
    marginRight: spacing.sm,
  },
  notificationButton: {
    minWidth: 48,
  },
  notificationButtonContent: {
    height: 48,
  },
  notificationBadge: {
    position: 'absolute',
    top: -8,
    right: -8,
  },
  categoriesSection: {
    marginBottom: spacing.md,
  },
  sectionTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  categoriesList: {
    paddingRight: spacing.md,
  },
  filterChip: {
    marginRight: spacing.sm,
  },
  filterChipText: {
    fontSize: 12,
  },
  statsContainer: {
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  statsText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  announcementCard: {
    marginBottom: spacing.md,
    borderRadius: borderRadius.md,
  },
  urgentCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
  },
  announcementHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  announcementTitle: {
    ...typography.h6,
    color: colors.text,
    flex: 1,
    marginRight: spacing.sm,
  },
  verifiedChip: {
    backgroundColor: colors.success + '20',
    borderColor: colors.success,
  },
  verifiedChipText: {
    color: colors.success,
    fontSize: 10,
  },
  announcementSummary: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    lineHeight: 20,
  },
  announcementMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  sourceName: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '500',
  },
  publishDate: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing.sm,
  },
  categoryChip: {
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
  },
  categoryChipText: {
    fontSize: 10,
  },
  deadlineContainer: {
    backgroundColor: colors.background,
    padding: spacing.sm,
    borderRadius: borderRadius.sm,
  },
  deadlineLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  deadlineText: {
    ...typography.body2,
    color: colors.text,
    fontWeight: '500',
  },
  urgentDeadlineText: {
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
  fab: {
    position: 'absolute',
    right: spacing.md,
    bottom: spacing.md,
  },
});

export default HomeScreen;
