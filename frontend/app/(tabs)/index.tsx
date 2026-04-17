import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../src/ThemeContext';
import { useAuth } from '../../src/AuthContext';
import { api } from '../../src/api';

export default function HomeScreen() {
  const { colors } = useTheme();
  const { user } = useAuth();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [verse, setVerse] = useState<any>(null);
  const [streak, setStreak] = useState<any>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [heatmap, setHeatmap] = useState<Record<string, number>>({});
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [v, s, d, h] = await Promise.all([
        api.getDailyVerse().catch(() => null),
        api.getStreak().catch(() => null),
        api.getDashboard().catch(() => null),
        api.getHeatmap().catch(() => ({ heatmap: {} })),
      ]);
      setVerse(v);
      setStreak(s);
      setDashboard(d);
      setHeatmap(h?.heatmap || {});
    } catch {} finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const onRefresh = () => { setRefreshing(true); loadData(); };

  // Generate last 91 days (13 weeks) for heat map
  const heatmapDays = [];
  const today = new Date();
  for (let i = 90; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = d.toISOString().split('T')[0];
    heatmapDays.push({ date: key, count: heatmap[key] || 0, day: d.getDay() });
  }

  function getHeatColor(count: number) {
    if (count === 0) return colors.muted;
    if (count === 1) return colors.primary + '40';
    if (count === 2) return colors.primary + '70';
    if (count <= 4) return colors.primary + 'B0';
    return colors.primary;
  }

  if (loading) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}>
      {/* Header */}
      <View style={styles.headerRow}>
        <View>
          <Text style={[styles.greeting, { color: colors.textSecondary }]}>Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening'},</Text>
          <Text style={[styles.userName, { color: colors.textPrimary }]}>{user?.name || 'Reader'}</Text>
        </View>
        <TouchableOpacity testID="mood-reading-btn" onPress={() => router.push('/mood')} style={[styles.moodBtn, { backgroundColor: colors.primary + '15' }]}>
          <Ionicons name="heart" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {/* Daily Verse */}
      {verse && (
        <View testID="daily-verse-card" style={[styles.verseCard, { backgroundColor: colors.primary }]}>
          <Text style={[styles.verseLabel, { color: colors.primaryForeground + 'B0' }]}>DAILY VERSE</Text>
          <Text style={[styles.verseText, { color: colors.primaryForeground }]}>{`"${verse.text}"`}</Text>
          <Text style={[styles.verseRef, { color: colors.primaryForeground + 'CC' }]}>— {verse.ref}</Text>
        </View>
      )}

      {/* Stats Row */}
      <View style={styles.statsRow}>
        <View testID="streak-tracker-widget" style={[styles.statCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Ionicons name="flame" size={24} color="#E8A365" />
          <Text style={[styles.statNum, { color: colors.textPrimary }]}>{streak?.current_streak || 0}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Day Streak</Text>
          {streak?.grace_day_available && (
            <View style={[styles.graceTag, { backgroundColor: colors.success + '20' }]}>
              <Ionicons name="leaf" size={10} color={colors.success} />
              <Text style={[styles.graceText, { color: colors.success }]}>Grace day available</Text>
            </View>
          )}
        </View>
        <View style={[styles.statCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Ionicons name="book" size={24} color={colors.primary} />
          <Text style={[styles.statNum, { color: colors.textPrimary }]}>{dashboard?.total_chapters_read || 0}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Chapters Read</Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <View style={[styles.statCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Ionicons name="calendar" size={24} color="#7B8EC4" />
          <Text style={[styles.statNum, { color: colors.textPrimary }]}>{dashboard?.active_plans || 0}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Active Plans</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Ionicons name="ribbon" size={24} color="#C47B7B" />
          <Text style={[styles.statNum, { color: colors.textPrimary }]}>{dashboard?.badges_earned || 0}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Badges</Text>
        </View>
      </View>

      {/* Heat Map */}
      <View testID="heatmap-widget" style={[styles.heatmapCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Reading Activity</Text>
        <Text style={[styles.heatmapSub, { color: colors.textSecondary }]}>Last 13 weeks</Text>
        <View style={styles.heatGrid}>
          {heatmapDays.map((d, i) => (
            <View key={i} style={[styles.heatCell, { backgroundColor: getHeatColor(d.count) }]} />
          ))}
        </View>
        <View style={styles.heatLegend}>
          <Text style={[styles.legendText, { color: colors.textSecondary }]}>Less</Text>
          {[0, 1, 2, 3, 5].map((c, i) => (
            <View key={i} style={[styles.legendCell, { backgroundColor: getHeatColor(c) }]} />
          ))}
          <Text style={[styles.legendText, { color: colors.textSecondary }]}>More</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity testID="quick-plans-btn" style={[styles.actionBtn, { backgroundColor: colors.surface, borderColor: colors.border }]} onPress={() => router.push('/(tabs)/plans')}>
          <Ionicons name="calendar-outline" size={22} color={colors.primary} />
          <Text style={[styles.actionText, { color: colors.textPrimary }]}>Reading Plans</Text>
          <Ionicons name="chevron-forward" size={16} color={colors.mutedForeground} />
        </TouchableOpacity>
        <TouchableOpacity testID="quick-map-btn" style={[styles.actionBtn, { backgroundColor: colors.surface, borderColor: colors.border }]} onPress={() => router.push('/(tabs)/map')}>
          <Ionicons name="grid-outline" size={22} color={colors.accent} />
          <Text style={[styles.actionText, { color: colors.textPrimary }]}>Bible Map</Text>
          <Ionicons name="chevron-forward" size={16} color={colors.mutedForeground} />
        </TouchableOpacity>
        <TouchableOpacity testID="quick-mood-btn" style={[styles.actionBtn, { backgroundColor: colors.surface, borderColor: colors.border }]} onPress={() => router.push('/mood')}>
          <Ionicons name="heart-outline" size={22} color="#C47B7B" />
          <Text style={[styles.actionText, { color: colors.textPrimary }]}>Mood Reading</Text>
          <Ionicons name="chevron-forward" size={16} color={colors.mutedForeground} />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 20, marginBottom: 20 },
  greeting: { fontSize: 14 },
  userName: { fontSize: 24, fontWeight: '700', marginTop: 2 },
  moodBtn: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
  verseCard: { marginHorizontal: 20, borderRadius: 20, padding: 24, marginBottom: 20 },
  verseLabel: { fontSize: 11, fontWeight: '700', letterSpacing: 1.5, marginBottom: 12 },
  verseText: { fontSize: 16, lineHeight: 26, fontStyle: 'italic', fontFamily: 'serif' },
  verseRef: { fontSize: 13, marginTop: 12, textAlign: 'right' },
  statsRow: { flexDirection: 'row', paddingHorizontal: 20, gap: 12, marginBottom: 12 },
  statCard: { flex: 1, borderRadius: 16, padding: 16, borderWidth: 1, alignItems: 'center' },
  statNum: { fontSize: 28, fontWeight: '700', marginTop: 6 },
  statLabel: { fontSize: 12, marginTop: 2 },
  graceTag: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, marginTop: 6 },
  graceText: { fontSize: 10, fontWeight: '600' },
  heatmapCard: { marginHorizontal: 20, borderRadius: 16, padding: 20, borderWidth: 1, marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: '600' },
  heatmapSub: { fontSize: 12, marginBottom: 12 },
  heatGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 3 },
  heatCell: { width: 12, height: 12, borderRadius: 3 },
  heatLegend: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 10 },
  legendCell: { width: 10, height: 10, borderRadius: 2 },
  legendText: { fontSize: 10 },
  quickActions: { paddingHorizontal: 20, gap: 8 },
  actionBtn: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 14, borderWidth: 1, gap: 12 },
  actionText: { flex: 1, fontSize: 15, fontWeight: '500' },
});
