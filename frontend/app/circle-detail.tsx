import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl, Alert, Share, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../src/ThemeContext';
import { useAuth } from '../src/AuthContext';
import { api } from '../src/api';

export default function CircleDetailScreen() {
  const { colors } = useTheme();
  const { user } = useAuth();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { circleId } = useLocalSearchParams<{ circleId: string }>();
  const [circle, setCircle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    if (!circleId) return;
    try {
      const data = await api.getCircleDetail(circleId);
      setCircle(data);
    } catch (e: any) {
      Alert.alert('Error', e.message);
      router.back();
    } finally { setLoading(false); setRefreshing(false); }
  }, [circleId]);

  useEffect(() => { loadData(); }, [loadData]);

  async function handleShare() {
    if (!circle?.invite_code) return;
    const message = `Join my Bible reading circle "${circle.name}" on VerseTrack!\n\nInvite code: ${circle.invite_code}`;
    try {
      await Share.share({ message });
    } catch {}
  }

  async function handleApprove(memberId: string) {
    try {
      await api.approveMember(circleId!, memberId);
      await loadData();
    } catch (e: any) { Alert.alert('Error', e.message); }
  }

  async function handleReject(memberId: string) {
    try {
      await api.rejectMember(circleId!, memberId);
      await loadData();
    } catch (e: any) { Alert.alert('Error', e.message); }
  }

  async function handleLeave() {
    Alert.alert('Leave Circle', 'Are you sure you want to leave this circle?', [
      { text: 'Cancel' },
      { text: 'Leave', style: 'destructive', onPress: async () => {
        try {
          await api.leaveCircle(circleId!);
          router.back();
        } catch (e: any) { Alert.alert('Error', e.message); }
      }},
    ]);
  }

  async function handleDelete() {
    Alert.alert('Delete Circle', 'This will permanently delete the circle for all members.', [
      { text: 'Cancel' },
      { text: 'Delete', style: 'destructive', onPress: async () => {
        try {
          await api.deleteCircle(circleId!);
          router.back();
        } catch (e: any) { Alert.alert('Error', e.message); }
      }},
    ]);
  }

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  if (!circle) return null;

  const members = circle.members_progress || [];
  const maxChapters = Math.max(...members.map((m: any) => m.total_chapters_read), 1);
  const pending = circle.pending_members || [];

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 40 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} tintColor={colors.primary} />}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity testID="circle-detail-back" onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={[styles.headerTitle, { color: colors.textPrimary }]}>{circle.name}</Text>
          <View style={styles.metaRow}>
            <Ionicons name={circle.privacy === 'public' ? 'globe-outline' : 'lock-closed-outline'} size={12} color={colors.mutedForeground} />
            <Text style={[styles.metaText, { color: colors.mutedForeground }]}>{circle.privacy === 'public' ? 'Public' : 'Private'} · {members.length} member{members.length !== 1 ? 's' : ''}</Text>
          </View>
        </View>
        <TouchableOpacity testID="circle-share-btn" onPress={handleShare} style={styles.shareBtn}>
          <Ionicons name="share-outline" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {circle.description ? <Text style={[styles.desc, { color: colors.textSecondary }]}>{circle.description}</Text> : null}

      {/* Invite Code Card */}
      <View style={[styles.inviteCard, { backgroundColor: colors.primary + '10', borderColor: colors.primary + '30' }]}>
        <Ionicons name="link" size={18} color={colors.primary} />
        <View style={{ flex: 1 }}>
          <Text style={[styles.inviteLabel, { color: colors.primary }]}>Invite Code</Text>
          <Text style={[styles.inviteCode, { color: colors.textPrimary }]}>{circle.invite_code}</Text>
        </View>
        <TouchableOpacity testID="share-invite-btn" onPress={handleShare} style={[styles.sharePill, { backgroundColor: colors.primary }]}>
          <Ionicons name="share-social" size={14} color={colors.primaryForeground} />
          <Text style={[styles.sharePillText, { color: colors.primaryForeground }]}>Share</Text>
        </TouchableOpacity>
      </View>

      {/* Member Progress */}
      <View style={[styles.progressCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Member Progress</Text>
        <Text style={[styles.sectionSub, { color: colors.textSecondary }]}>
          {circle.plan_mode === 'shared' ? 'Shared plan progress' : 'Total chapters read'}
        </Text>

        {members.map((m: any, i: number) => {
          const isShared = circle.plan_mode === 'shared' && m.plan_progress;
          const barValue = isShared ? m.plan_progress.percent : Math.min((m.total_chapters_read / maxChapters) * 100, 100);
          const barLabel = isShared ? `${m.plan_progress.completed}/${m.plan_progress.total} chapters (${m.plan_progress.percent}%)` : `${m.total_chapters_read} chapters read`;
          const isMe = m.user_id === user?.id;
          return (
            <View key={m.user_id} testID={`member-progress-${i}`} style={styles.memberRow}>
              <View style={styles.memberInfo}>
                <View style={[styles.memberAvatar, { backgroundColor: isMe ? colors.primary : colors.accent + '40' }]}>
                  <Text style={[styles.memberInitial, { color: isMe ? colors.primaryForeground : colors.textPrimary }]}>{(m.name || '?')[0].toUpperCase()}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <View style={styles.nameRow}>
                    <Text style={[styles.memberName, { color: colors.textPrimary }]}>{m.name}{isMe ? ' (You)' : ''}</Text>
                    {m.role === 'creator' && (
                      <View style={[styles.creatorBadge, { backgroundColor: colors.accent + '20' }]}>
                        <Text style={[styles.creatorBadgeText, { color: colors.accent }]}>Creator</Text>
                      </View>
                    )}
                  </View>
                  <View style={styles.streakRow}>
                    <Ionicons name="flame" size={12} color="#E8A365" />
                    <Text style={[styles.streakText, { color: colors.mutedForeground }]}>{m.current_streak} day streak</Text>
                  </View>
                </View>
              </View>
              {/* Progress Bar */}
              <View style={styles.barContainer}>
                <View style={[styles.barBg, { backgroundColor: colors.muted }]}>
                  <View style={[styles.barFill, { width: `${Math.max(barValue, 2)}%`, backgroundColor: isMe ? colors.primary : colors.accent }]} />
                </View>
                <Text style={[styles.barLabel, { color: colors.textSecondary }]}>{barLabel}</Text>
              </View>
            </View>
          );
        })}
      </View>

      {/* Pending Members (creator only) */}
      {circle.is_creator && pending.length > 0 && (
        <View style={[styles.pendingCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Pending Requests</Text>
          {pending.map((m: any) => (
            <View key={m.user_id} testID={`pending-member-${m.user_id}`} style={styles.pendingRow}>
              <View style={[styles.memberAvatar, { backgroundColor: colors.muted }]}>
                <Text style={[styles.memberInitial, { color: colors.textSecondary }]}>{(m.name || '?')[0].toUpperCase()}</Text>
              </View>
              <Text style={[styles.pendingName, { color: colors.textPrimary }]}>{m.name}</Text>
              <TouchableOpacity testID={`approve-${m.user_id}`} style={[styles.approvBtn, { backgroundColor: colors.success + '20' }]} onPress={() => handleApprove(m.user_id)}>
                <Ionicons name="checkmark" size={16} color={colors.success} />
              </TouchableOpacity>
              <TouchableOpacity testID={`reject-${m.user_id}`} style={[styles.rejectBtn, { backgroundColor: colors.danger + '20' }]} onPress={() => handleReject(m.user_id)}>
                <Ionicons name="close" size={16} color={colors.danger} />
              </TouchableOpacity>
            </View>
          ))}
        </View>
      )}

      {/* Actions */}
      <View style={styles.actionsSection}>
        {circle.is_creator ? (
          <TouchableOpacity testID="delete-circle-btn" style={[styles.dangerBtn, { borderColor: colors.danger }]} onPress={handleDelete}>
            <Ionicons name="trash-outline" size={16} color={colors.danger} />
            <Text style={[styles.dangerBtnText, { color: colors.danger }]}>Delete Circle</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity testID="leave-circle-btn" style={[styles.dangerBtn, { borderColor: colors.danger }]} onPress={handleLeave}>
            <Ionicons name="exit-outline" size={16} color={colors.danger} />
            <Text style={[styles.dangerBtnText, { color: colors.danger }]}>Leave Circle</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  headerRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, marginBottom: 8, gap: 8 },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerCenter: { flex: 1 },
  headerTitle: { fontSize: 22, fontWeight: '700' },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 2 },
  metaText: { fontSize: 12 },
  shareBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  desc: { fontSize: 14, paddingHorizontal: 20, marginBottom: 16, lineHeight: 20 },
  inviteCard: { flexDirection: 'row', alignItems: 'center', marginHorizontal: 20, borderRadius: 14, borderWidth: 1, padding: 16, gap: 12, marginBottom: 16 },
  inviteLabel: { fontSize: 11, fontWeight: '600', letterSpacing: 0.5 },
  inviteCode: { fontSize: 20, fontWeight: '700', letterSpacing: 2 },
  sharePill: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20 },
  sharePillText: { fontSize: 12, fontWeight: '600' },
  progressCard: { marginHorizontal: 20, borderRadius: 16, borderWidth: 1, padding: 20, marginBottom: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '600' },
  sectionSub: { fontSize: 12, marginBottom: 16 },
  memberRow: { marginBottom: 18 },
  memberInfo: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 8 },
  memberAvatar: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  memberInitial: { fontSize: 15, fontWeight: '700' },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  memberName: { fontSize: 14, fontWeight: '600' },
  creatorBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  creatorBadgeText: { fontSize: 10, fontWeight: '600' },
  streakRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 1 },
  streakText: { fontSize: 11 },
  barContainer: { paddingLeft: 46 },
  barBg: { height: 10, borderRadius: 5, overflow: 'hidden' },
  barFill: { height: '100%', borderRadius: 5 },
  barLabel: { fontSize: 11, marginTop: 4 },
  pendingCard: { marginHorizontal: 20, borderRadius: 16, borderWidth: 1, padding: 20, marginBottom: 16 },
  pendingRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 12 },
  pendingName: { flex: 1, fontSize: 14, fontWeight: '500' },
  approvBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  rejectBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  actionsSection: { paddingHorizontal: 20, marginTop: 8 },
  dangerBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 14, borderWidth: 1 },
  dangerBtnText: { fontSize: 14, fontWeight: '600' },
});
