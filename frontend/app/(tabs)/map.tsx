import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../src/ThemeContext';
import { api } from '../../src/api';

const STATUS_COLORS = {
  completed: '#8BA888',
  in_progress: '#E8A365',
  unread: 'transparent',
};

export default function BibleMapScreen() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [books, setBooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'OT' | 'NT'>('all');

  const loadData = useCallback(async () => {
    try {
      const data = await api.getBooksStatus();
      setBooks(data.books || []);
    } catch {} finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const filtered = filter === 'all' ? books : books.filter(b => b.testament === filter);
  const completed = books.filter(b => b.status === 'completed').length;
  const inProgress = books.filter(b => b.status === 'in_progress').length;

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} tintColor={colors.primary} />}>
      <Text style={[styles.screenTitle, { color: colors.textPrimary }]}>Bible Map</Text>

      {/* Summary */}
      <View style={[styles.summaryRow, { paddingHorizontal: 20 }]}>
        <View style={[styles.summaryChip, { backgroundColor: STATUS_COLORS.completed + '20' }]}>
          <View style={[styles.dot, { backgroundColor: STATUS_COLORS.completed }]} />
          <Text style={[styles.chipText, { color: colors.textPrimary }]}>{completed} Completed</Text>
        </View>
        <View style={[styles.summaryChip, { backgroundColor: STATUS_COLORS.in_progress + '20' }]}>
          <View style={[styles.dot, { backgroundColor: STATUS_COLORS.in_progress }]} />
          <Text style={[styles.chipText, { color: colors.textPrimary }]}>{inProgress} In Progress</Text>
        </View>
        <View style={[styles.summaryChip, { backgroundColor: colors.muted }]}>
          <View style={[styles.dot, { backgroundColor: colors.mutedForeground }]} />
          <Text style={[styles.chipText, { color: colors.textPrimary }]}>{66 - completed - inProgress} Unread</Text>
        </View>
      </View>

      {/* Filter */}
      <View style={[styles.filterRow, { paddingHorizontal: 20 }]}>
        {(['all', 'OT', 'NT'] as const).map(f => (
          <TouchableOpacity key={f} testID={`filter-${f}`} style={[styles.filterBtn, filter === f && { backgroundColor: colors.primary }]} onPress={() => setFilter(f)}>
            <Text style={[styles.filterText, { color: filter === f ? colors.primaryForeground : colors.textSecondary }]}>
              {f === 'all' ? 'All' : f === 'OT' ? 'Old Testament' : 'New Testament'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Books Grid */}
      <View style={styles.grid}>
        {filtered.map(book => {
          const bgColor = book.status === 'completed' ? colors.primary : book.status === 'in_progress' ? colors.accent + '30' : colors.muted;
          const textColor = book.status === 'completed' ? colors.primaryForeground : colors.textPrimary;
          const borderColor = book.status === 'in_progress' ? colors.accent : book.status === 'completed' ? colors.primary : colors.border;
          return (
            <TouchableOpacity
              key={book.slug}
              testID={`bible-book-button-${book.slug}`}
              style={[styles.bookBtn, { backgroundColor: bgColor, borderColor }]}
              onPress={() => router.push({ pathname: '/reader', params: { bookSlug: book.slug, chapter: 1, version: 'kjv' } })}
            >
              <Text style={[styles.bookAbbr, { color: textColor }]}>{book.abbr}</Text>
              <Text style={[styles.bookProgress, { color: book.status === 'completed' ? textColor + 'CC' : colors.textSecondary }]}>
                {book.read}/{book.chapters}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  screenTitle: { fontSize: 28, fontWeight: '700', paddingHorizontal: 20, marginBottom: 16 },
  summaryRow: { flexDirection: 'row', gap: 8, marginBottom: 16, flexWrap: 'wrap' },
  summaryChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  chipText: { fontSize: 12, fontWeight: '500' },
  filterRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  filterBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
  filterText: { fontSize: 13, fontWeight: '500' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 16, gap: 8 },
  bookBtn: { width: '22%', aspectRatio: 1, borderRadius: 12, borderWidth: 1, justifyContent: 'center', alignItems: 'center', padding: 4 },
  bookAbbr: { fontSize: 13, fontWeight: '700' },
  bookProgress: { fontSize: 9, marginTop: 2 },
});
