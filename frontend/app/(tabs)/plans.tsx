import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../src/ThemeContext';
import { api } from '../../src/api';

const PLAN_ICONS: Record<string, string> = {
  'book': 'book', 'zap': 'flash', 'lightbulb': 'bulb', 'crown': 'diamond', 'heart': 'heart',
};

export default function PlansScreen() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [plans, setPlans] = useState<any[]>([]);
  const [activePlans, setActivePlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [tab, setTab] = useState<'browse' | 'active'>('browse');

  const loadData = useCallback(async () => {
    try {
      const [p, a] = await Promise.all([api.getPlans(), api.getActivePlans()]);
      setPlans(p.plans || []);
      setActivePlans(a.plans || []);
    } catch {} finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  async function handleActivate(planId: string) {
    setActivating(planId);
    try {
      await api.activatePlan(planId);
      await loadData();
      setTab('active');
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally { setActivating(''); }
  }

  async function handleRecalculate(planDocId: string) {
    try {
      const result = await api.recalculatePlan(planDocId);
      Alert.alert('Plan Recalculated', result.message);
      await loadData();
    } catch (e: any) {
      Alert.alert('Error', e.message);
    }
  }

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  const activeIds = activePlans.map(p => p.plan_id);

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} tintColor={colors.primary} />}>
      <Text style={[styles.screenTitle, { color: colors.textPrimary }]}>Reading Plans</Text>

      {/* Tab Switcher */}
      <View style={[styles.tabRow, { backgroundColor: colors.muted }]}>
        <TouchableOpacity testID="plans-browse-tab" style={[styles.tabBtn, tab === 'browse' && { backgroundColor: colors.surface }]} onPress={() => setTab('browse')}>
          <Text style={[styles.tabText, { color: tab === 'browse' ? colors.textPrimary : colors.textSecondary }]}>Browse Plans</Text>
        </TouchableOpacity>
        <TouchableOpacity testID="plans-active-tab" style={[styles.tabBtn, tab === 'active' && { backgroundColor: colors.surface }]} onPress={() => setTab('active')}>
          <Text style={[styles.tabText, { color: tab === 'active' ? colors.textPrimary : colors.textSecondary }]}>Active ({activePlans.length})</Text>
        </TouchableOpacity>
      </View>

      {tab === 'browse' ? (
        <View style={styles.section}>
          {plans.map(plan => {
            const isActive = activeIds.includes(plan.id);
            const iconName = PLAN_ICONS[plan.icon] || 'book';
            return (
              <View key={plan.id} style={[styles.planCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                <View style={[styles.planIcon, { backgroundColor: plan.color + '20' }]}>
                  <Ionicons name={iconName as any} size={22} color={plan.color} />
                </View>
                <View style={styles.planInfo}>
                  <Text style={[styles.planName, { color: colors.textPrimary }]}>{plan.name}</Text>
                  <Text style={[styles.planDesc, { color: colors.textSecondary }]} numberOfLines={2}>{plan.description}</Text>
                  <Text style={[styles.planDuration, { color: colors.mutedForeground }]}>{plan.duration_days} days</Text>
                </View>
                <TouchableOpacity
                  testID={`activate-plan-${plan.id}`}
                  style={[styles.activateBtn, { backgroundColor: isActive ? colors.muted : colors.primary }]}
                  onPress={() => !isActive && handleActivate(plan.id)}
                  disabled={isActive || activating === plan.id}
                >
                  {activating === plan.id ? <ActivityIndicator size="small" color={colors.primaryForeground} /> :
                    <Text style={{ color: isActive ? colors.textSecondary : colors.primaryForeground, fontSize: 13, fontWeight: '600' }}>{isActive ? 'Active' : 'Start'}</Text>}
                </TouchableOpacity>
              </View>
            );
          })}
        </View>
      ) : (
        <View style={styles.section}>
          {activePlans.length === 0 ? (
            <View style={[styles.emptyCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
              <Ionicons name="calendar-outline" size={40} color={colors.mutedForeground} />
              <Text style={[styles.emptyText, { color: colors.textSecondary }]}>No active plans yet</Text>
              <TouchableOpacity onPress={() => setTab('browse')}>
                <Text style={{ color: colors.primary, fontWeight: '600' }}>Browse plans</Text>
              </TouchableOpacity>
            </View>
          ) : activePlans.map(plan => {
            const progress = plan.total_chapters > 0 ? (plan.completed_chapters / plan.total_chapters) : 0;
            const pct = Math.round(progress * 100);
            return (
              <View key={plan.id} style={[styles.activePlanCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
                <View style={styles.activePlanHeader}>
                  <Text style={[styles.planName, { color: colors.textPrimary }]}>{plan.plan_name}</Text>
                  <Text style={[styles.pctText, { color: colors.primary }]}>{pct}%</Text>
                </View>
                <View style={[styles.progressBar, { backgroundColor: colors.muted }]}>
                  <View style={[styles.progressFill, { width: `${pct}%`, backgroundColor: colors.primary }]} />
                </View>
                <Text style={[styles.progressDetail, { color: colors.textSecondary }]}>{plan.completed_chapters} of {plan.total_chapters} chapters</Text>
                <View style={styles.activePlanActions}>
                  <TouchableOpacity testID={`continue-reading-${plan.id}`} style={[styles.continueBtn, { backgroundColor: colors.primary }]} onPress={() => {
                    // Find next unread chapter
                    const assignments = plan.daily_assignments || [];
                    for (const day of assignments) {
                      if (!day.completed && day.chapters?.length > 0) {
                        const ch = day.chapters[0];
                        router.push({ pathname: '/reader', params: { bookSlug: ch.book_slug, chapter: ch.chapter, planId: plan.id, version: 'kjv' } });
                        return;
                      }
                    }
                  }}>
                    <Ionicons name="play" size={14} color={colors.primaryForeground} />
                    <Text style={[styles.continueBtnText, { color: colors.primaryForeground }]}>Continue</Text>
                  </TouchableOpacity>
                  <TouchableOpacity testID={`recalculate-plan-${plan.id}`} style={[styles.recalcBtn, { borderColor: colors.border }]} onPress={() => handleRecalculate(plan.id)}>
                    <Ionicons name="refresh" size={14} color={colors.textSecondary} />
                    <Text style={[styles.recalcText, { color: colors.textSecondary }]}>Recalculate</Text>
                  </TouchableOpacity>
                </View>
              </View>
            );
          })}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  screenTitle: { fontSize: 28, fontWeight: '700', paddingHorizontal: 20, marginBottom: 16 },
  tabRow: { flexDirection: 'row', marginHorizontal: 20, borderRadius: 12, padding: 4, marginBottom: 16 },
  tabBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
  tabText: { fontSize: 14, fontWeight: '600' },
  section: { paddingHorizontal: 20, gap: 12 },
  planCard: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 16, borderWidth: 1, gap: 12 },
  planIcon: { width: 44, height: 44, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  planInfo: { flex: 1 },
  planName: { fontSize: 16, fontWeight: '600' },
  planDesc: { fontSize: 12, marginTop: 2, lineHeight: 18 },
  planDuration: { fontSize: 11, marginTop: 4 },
  activateBtn: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  emptyCard: { alignItems: 'center', padding: 40, borderRadius: 16, borderWidth: 1, gap: 12 },
  emptyText: { fontSize: 15 },
  activePlanCard: { padding: 20, borderRadius: 16, borderWidth: 1 },
  activePlanHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  pctText: { fontSize: 20, fontWeight: '700' },
  progressBar: { height: 8, borderRadius: 4, overflow: 'hidden', marginBottom: 8 },
  progressFill: { height: '100%', borderRadius: 4 },
  progressDetail: { fontSize: 12, marginBottom: 12 },
  activePlanActions: { flexDirection: 'row', gap: 8 },
  continueBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20 },
  continueBtnText: { fontSize: 13, fontWeight: '600' },
  recalcBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, borderWidth: 1 },
  recalcText: { fontSize: 13 },
});
