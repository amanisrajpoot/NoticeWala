/**
 * Search Screen for NoticeWala Mobile App
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import {
  Text,
  Card,
  Chip,
  Searchbar,
  Button,
  SegmentedButtons,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import {
  fetchAnnouncements,
  setFilters,
  clearAnnouncements,
} from '@store/slices/announcementSlice';
import { colors, spacing, borderRadius, typography } from '@utils/theme';
import {
  formatDate,
  getTimeUntilDeadline,
  isDeadlineUrgent,
  getCategoryColor,
  getCategoryDisplayName,
} from '@utils/helpers';
import { Announcement } from '@store/slices/announcementSlice';

const SearchScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  
  const {
    announcements,
    categories,
    sources,
    filters,
    isLoading,
    hasMore,
    totalCount,
  } = useAppSelector((state) => state.announcements);
  
  const [searchQuery, setSearchQuery] = useState(filters.search || '');
  const [selectedCategory, setSelectedCategory] = useState(filters.category || '');
  const [sortBy, setSortBy] = useState(filters.sort_by || 'created_at');
  const [sortOrder, setSortOrder] = useState(filters.sort_order || 'desc');

  const sortOptions = [
    { value: 'created_at', label: 'Date' },
    { value: 'priority_score', label: 'Priority' },
    { value: 'title', label: 'Title' },
  ];

  const orderOptions = [
    { value: 'desc', label: 'Newest' },
    { value: 'asc', label: 'Oldest' },
  ];

  const performSearch = useCallback(async () => {
    dispatch(clearAnnouncements());
    
    const newFilters = {
      search: searchQuery.trim() || undefined,
      category: selectedCategory || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
      skip: 0,
      limit: 20,
    };
    
    dispatch(setFilters(newFilters));
    await dispatch(fetchAnnouncements(newFilters));
  }, [searchQuery, selectedCategory, sortBy, sortOrder, dispatch]);

  const loadMore = useCallback(async () => {
    if (!hasMore || isLoading) return;
    
    const newFilters = {
      ...filters,
      skip: announcements.length,
    };
    
    await dispatch(fetchAnnouncements(newFilters));
  }, [hasMore, isLoading, filters, announcements.length, dispatch]);

  const handleSearch = useCallback(() => {
    performSearch();
  }, [performSearch]);

  const handleCategorySelect = useCallback((category: string) => {
    setSelectedCategory(category === selectedCategory ? '' : category);
  }, [selectedCategory]);

  const handleSortChange = useCallback((value: string) => {
    setSortBy(value);
  }, []);

  const handleOrderChange = useCallback((value: string) => {
    setSortOrder(value);
  }, []);

  const clearFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedCategory('');
    setSortBy('created_at');
    setSortOrder('desc');
  }, []);

  const renderAnnouncementItem = ({ item }: { item: Announcement }) => {
    const isUrgent = item.application_deadline 
      ? isDeadlineUrgent(item.application_deadline)
      : false;

    return (
      <Card style={[styles.announcementCard, isUrgent && styles.urgentCard]}>
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
      onPress={() => handleCategorySelect(item)}
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
      <Searchbar
        placeholder="Search announcements..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        onSubmitEditing={handleSearch}
        style={styles.searchbar}
      />

      <View style={styles.filtersContainer}>
        <View style={styles.filterRow}>
          <Text style={styles.filterLabel}>Sort by:</Text>
          <SegmentedButtons
            value={sortBy}
            onValueChange={handleSortChange}
            buttons={sortOptions}
            style={styles.segmentedButtons}
          />
        </View>

        <View style={styles.filterRow}>
          <Text style={styles.filterLabel}>Order:</Text>
          <SegmentedButtons
            value={sortOrder}
            onValueChange={handleOrderChange}
            buttons={orderOptions}
            style={styles.segmentedButtons}
          />
        </View>
      </View>

      {categories.length > 0 && (
        <View style={styles.categoriesSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Categories</Text>
            <Button
              mode="text"
              onPress={clearFilters}
              compact
              labelStyle={styles.clearButtonText}
            >
              Clear All
            </Button>
          </View>
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

      <Button
        mode="contained"
        onPress={handleSearch}
        style={styles.searchButton}
        loading={isLoading}
        disabled={isLoading}
      >
        Search
      </Button>
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
        Try adjusting your search criteria
      </Text>
      <Button
        mode="outlined"
        onPress={clearFilters}
        style={styles.emptyButton}
      >
        Clear Filters
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
        onEndReached={loadMore}
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
  searchbar: {
    marginBottom: spacing.md,
  },
  filtersContainer: {
    marginBottom: spacing.md,
  },
  filterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  filterLabel: {
    ...typography.body2,
    color: colors.text,
    marginRight: spacing.sm,
    minWidth: 60,
  },
  segmentedButtons: {
    flex: 1,
  },
  categoriesSection: {
    marginBottom: spacing.md,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.h6,
    color: colors.text,
  },
  clearButtonText: {
    fontSize: 12,
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
  searchButton: {
    marginBottom: spacing.md,
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
});

export default SearchScreen;
