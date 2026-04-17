import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Switch, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../src/ThemeContext';
import { useAuth } from '../../src/AuthContext';
import { api } from '../../src/api';

const BADGE_ICONS: Record<string, string> = {
  scroll: 'document-text', landmark: 'business', brain: 'bulb', megaphone: 'megaphone',
  'message-circle': 'chatbubble', heart: 'heart', mail: 'mail', 'book-open': 'book',
  star: 'star', award: 'trophy', flame: 'flame', eye: 'eye',
};

export default function ProfileScreen() {
  const { colors, mode, isDark, setMode } = useTheme();
  const { user, logout } = useAuth();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [badges, setBadges] = useState<any[]>([]);
  const [streak, setStreak] = useState<any>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [b, s, d] = await Promise.all([api.getBadges(), api.getStreak(), api.getDashboard()]);
      setBadges(b.badges || []);
      setStreak(s);
      setDashboard(d);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  async function handleLogout() {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: async () => { await logout(); router.replace('/(auth)/login'); } },
    ]);
  }

  const earnedBadges = badges.filter(b => b.earned);
  const lockedBadges = badges.filter(b => !b.earned);

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 40 }}>
      <Text style={[styles.screenTitle, { color: colors.textPrimary }]}>Profile</Text>

      {/* User Card */}
      <View style={[styles.userCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
          <Text style={[styles.avatarText, { color: colors.primaryForeground }]}>{(user?.name || 'U')[0].toUpperCase()}</Text>
        </View>
        <Text style={[styles.nameText, { color: colors.textPrimary }]}>{user?.name}</Text>
        <Text style={[styles.emailText, { color: colors.textSecondary }]}>{user?.email}</Text>
        <View style={styles.userStats}>
          <View style={styles.userStat}>
            <Text style={[styles.userStatNum, { color: colors.textPrimary }]}>{streak?.total_days_read || 0}</Text>
            <Text style={[styles.userStatLabel, { color: colors.textSecondary }]}>Days Read</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: colors.border }]} />
          <View style={styles.userStat}>
            <Text style={[styles.userStatNum, { color: colors.textPrimary }]}>{dashboard?.total_chapters_read || 0}</Text>
            <Text style={[styles.userStatLabel, { color: colors.textSecondary }]}>Chapters</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: colors.border }]} />
          <View style={styles.userStat}>
            <Text style={[styles.userStatNum, { color: colors.textPrimary }]}>{streak?.longest_streak || 0}</Text>
            <Text style={[styles.userStatLabel, { color: colors.textSecondary }]}>Best Streak</Text>
          </View>
        </View>
      </View>

      {/* Theme Settings */}
      <View style={[styles.settingsCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Appearance</Text>
        <View style={styles.themeOptions}>
          {(['auto', 'light', 'dark'] as const).map(m => (
            <TouchableOpacity key={m} testID={`theme-toggle-${m}`} style={[styles.themeBtn, mode === m && { backgroundColor: colors.primary + '20', borderColor: colors.primary }]} onPress={() => setMode(m)}>
              <Ionicons name={m === 'auto' ? 'phone-portrait' : m === 'light' ? 'sunny' : 'moon'} size={18} color={mode === m ? colors.primary : colors.mutedForeground} />
              <Text style={[styles.themeBtnText, { color: mode === m ? colors.primary : colors.textSecondary }]}>{m === 'auto' ? 'Auto' : m === 'light' ? 'Light' : 'Dark'}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Badges */}
      <View style={[styles.badgesCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Milestones & Badges</Text>
        <Text style={[styles.badgeSub, { color: colors.textSecondary }]}>{earnedBadges.length} of {badges.length} earned</Text>

        {earnedBadges.length > 0 && (
          <View style={styles.badgeGrid}>
            {earnedBadges.map(b => (
              <View key={b.id} style={[styles.badgeItem, { backgroundColor: b.color + '15' }]}>
                <Ionicons name={(BADGE_ICONS[b.icon] || 'star') as any} size={22} color={b.color} />
                <Text style={[styles.badgeName, { color: colors.textPrimary }]} numberOfLines={1}>{b.name}</Text>
              </View>
            ))}
          </View>
        )}

        {lockedBadges.length > 0 && (
          <>
            <Text style={[styles.lockedLabel, { color: colors.mutedForeground }]}>Locked</Text>
            <View style={styles.badgeGrid}>
              {lockedBadges.map(b => (
                <View key={b.id} style={[styles.badgeItem, { backgroundColor: colors.muted, opacity: 0.6 }]}>
                  <Ionicons name="lock-closed" size={18} color={colors.mutedForeground} />
                  <Text style={[styles.badgeName, { color: colors.mutedForeground }]} numberOfLines={1}>{b.name}</Text>
                </View>
              ))}
            </View>
          </>
        )}
      </View>

      {/* Sign Out */}
      <TouchableOpacity testID="sign-out-btn" style={[styles.logoutBtn, { borderColor: colors.danger }]} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={18} color={colors.danger} />
        <Text style={[styles.logoutText, { color: colors.danger }]}>Sign Out</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  screenTitle: { fontSize: 28, fontWeight: '700', paddingHorizontal: 20, marginBottom: 16 },
  userCard: { marginHorizontal: 20, borderRadius: 20, padding: 24, borderWidth: 1, alignItems: 'center', marginBottom: 16 },
  avatar: { width: 64, height: 64, borderRadius: 32, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  avatarText: { fontSize: 26, fontWeight: '700' },
  nameText: { fontSize: 20, fontWeight: '600' },
  emailText: { fontSize: 13, marginTop: 2 },
  userStats: { flexDirection: 'row', marginTop: 20, gap: 20 },
  userStat: { alignItems: 'center' },
  userStatNum: { fontSize: 22, fontWeight: '700' },
  userStatLabel: { fontSize: 11, marginTop: 2 },
  statDivider: { width: 1, height: 36, alignSelf: 'center' },
  settingsCard: { marginHorizontal: 20, borderRadius: 16, padding: 20, borderWidth: 1, marginBottom: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  themeOptions: { flexDirection: 'row', gap: 8 },
  themeBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, paddingVertical: 12, borderRadius: 12, borderWidth: 1, borderColor: 'transparent' },
  themeBtnText: { fontSize: 13, fontWeight: '500' },
  badgesCard: { marginHorizontal: 20, borderRadius: 16, padding: 20, borderWidth: 1, marginBottom: 16 },
  badgeSub: { fontSize: 12, marginBottom: 12 },
  badgeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  badgeItem: { width: '30%', borderRadius: 12, padding: 12, alignItems: 'center', gap: 6 },
  badgeName: { fontSize: 10, fontWeight: '600', textAlign: 'center' },
  lockedLabel: { fontSize: 12, fontWeight: '500', marginTop: 12, marginBottom: 8 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginHorizontal: 20, padding: 16, borderRadius: 14, borderWidth: 1 },
  logoutText: { fontSize: 15, fontWeight: '600' },
});
