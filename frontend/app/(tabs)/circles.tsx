import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl, TextInput, Modal, Alert, Share, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../src/ThemeContext';
import { api } from '../../src/api';

export default function CirclesScreen() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [circles, setCircles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [showJoin, setShowJoin] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [joining, setJoining] = useState(false);
  // Create form
  const [cName, setCName] = useState('');
  const [cDesc, setCDesc] = useState('');
  const [cPrivacy, setCPrivacy] = useState<'public' | 'private'>('public');
  const [cPlanMode, setCPlanMode] = useState<'individual' | 'shared'>('individual');
  const [creating, setCreating] = useState(false);
  // Plans for shared mode
  const [plans, setPlans] = useState<any[]>([]);
  const [selectedPlan, setSelectedPlan] = useState('');

  const loadData = useCallback(async () => {
    try {
      const [c, p] = await Promise.all([api.getMyCircles(), api.getPlans()]);
      setCircles(c.circles || []);
      setPlans(p.plans || []);
    } catch {} finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  async function handleCreate() {
    if (!cName.trim()) { Alert.alert('Error', 'Please enter a circle name'); return; }
    setCreating(true);
    try {
      await api.createCircle(cName.trim(), cDesc.trim(), cPrivacy, cPlanMode, cPlanMode === 'shared' ? selectedPlan : undefined);
      setShowCreate(false);
      setCName(''); setCDesc(''); setCPrivacy('public'); setCPlanMode('individual'); setSelectedPlan('');
      await loadData();
    } catch (e: any) { Alert.alert('Error', e.message); }
    finally { setCreating(false); }
  }

  async function handleJoin() {
    if (!joinCode.trim()) { Alert.alert('Error', 'Please enter an invite code'); return; }
    setJoining(true);
    try {
      const result = await api.joinCircle(joinCode.trim().toUpperCase());
      Alert.alert('Success', result.message);
      setShowJoin(false); setJoinCode('');
      await loadData();
    } catch (e: any) { Alert.alert('Error', e.message); }
    finally { setJoining(false); }
  }

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <ScrollView contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} tintColor={colors.primary} />}>
        <Text style={[styles.screenTitle, { color: colors.textPrimary }]}>Reading Circles</Text>
        <Text style={[styles.screenSub, { color: colors.textSecondary }]}>Read together, grow together</Text>

        {/* Action Buttons */}
        <View style={styles.actionRow}>
          <TouchableOpacity testID="create-circle-btn" style={[styles.actionBtn, { backgroundColor: colors.primary }]} onPress={() => setShowCreate(true)}>
            <Ionicons name="add-circle" size={18} color={colors.primaryForeground} />
            <Text style={[styles.actionBtnText, { color: colors.primaryForeground }]}>Create Circle</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="join-circle-btn" style={[styles.actionBtn, { backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1 }]} onPress={() => setShowJoin(true)}>
            <Ionicons name="enter-outline" size={18} color={colors.textPrimary} />
            <Text style={[styles.actionBtnText, { color: colors.textPrimary }]}>Join Circle</Text>
          </TouchableOpacity>
        </View>

        {/* Circles List */}
        {circles.length === 0 ? (
          <View style={[styles.emptyCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <Ionicons name="people-outline" size={48} color={colors.mutedForeground} />
            <Text style={[styles.emptyTitle, { color: colors.textPrimary }]}>No circles yet</Text>
            <Text style={[styles.emptyText, { color: colors.textSecondary }]}>Create a circle or join one with an invite code</Text>
          </View>
        ) : circles.map(circle => (
          <TouchableOpacity
            key={circle.id}
            testID={`circle-card-${circle.id}`}
            style={[styles.circleCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
            onPress={() => router.push({ pathname: '/circle-detail', params: { circleId: circle.id } })}
          >
            <View style={styles.circleCardHeader}>
              <View style={[styles.circleIcon, { backgroundColor: colors.primary + '20' }]}>
                <Ionicons name="people" size={22} color={colors.primary} />
              </View>
              <View style={styles.circleInfo}>
                <Text style={[styles.circleName, { color: colors.textPrimary }]}>{circle.name}</Text>
                <View style={styles.circleMetaRow}>
                  <Ionicons name={circle.privacy === 'public' ? 'globe-outline' : 'lock-closed-outline'} size={12} color={colors.mutedForeground} />
                  <Text style={[styles.circleMeta, { color: colors.mutedForeground }]}>{circle.privacy === 'public' ? 'Public' : 'Private'}</Text>
                  <Text style={[styles.circleMeta, { color: colors.mutedForeground }]}> · </Text>
                  <Ionicons name="people-outline" size={12} color={colors.mutedForeground} />
                  <Text style={[styles.circleMeta, { color: colors.mutedForeground }]}>{circle.member_count} member{circle.member_count !== 1 ? 's' : ''}</Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.mutedForeground} />
            </View>
            {circle.description ? <Text style={[styles.circleDesc, { color: colors.textSecondary }]} numberOfLines={2}>{circle.description}</Text> : null}
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Create Circle Modal */}
      <Modal visible={showCreate} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: colors.background, borderColor: colors.border }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.textPrimary }]}>Create Reading Circle</Text>
              <TouchableOpacity testID="close-create-modal" onPress={() => setShowCreate(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.modalScroll}>
              <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>Circle Name *</Text>
              <TextInput testID="circle-name-input" style={[styles.fieldInput, { backgroundColor: colors.muted, borderColor: colors.border, color: colors.textPrimary }]} placeholder="e.g., Sunday School Group" placeholderTextColor={colors.mutedForeground} value={cName} onChangeText={setCName} />

              <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>Description</Text>
              <TextInput testID="circle-desc-input" style={[styles.fieldInput, styles.multiline, { backgroundColor: colors.muted, borderColor: colors.border, color: colors.textPrimary }]} placeholder="What's this circle about?" placeholderTextColor={colors.mutedForeground} value={cDesc} onChangeText={setCDesc} multiline />

              <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>Privacy</Text>
              <View style={styles.toggleRow}>
                {(['public', 'private'] as const).map(p => (
                  <TouchableOpacity key={p} testID={`privacy-${p}`} style={[styles.toggleBtn, cPrivacy === p && { backgroundColor: colors.primary + '20', borderColor: colors.primary }]} onPress={() => setCPrivacy(p)}>
                    <Ionicons name={p === 'public' ? 'globe-outline' : 'lock-closed-outline'} size={16} color={cPrivacy === p ? colors.primary : colors.textSecondary} />
                    <Text style={[styles.toggleText, { color: cPrivacy === p ? colors.primary : colors.textSecondary }]}>{p === 'public' ? 'Public' : 'Private'}</Text>
                  </TouchableOpacity>
                ))}
              </View>
              <Text style={[styles.fieldHint, { color: colors.mutedForeground }]}>{cPrivacy === 'public' ? 'Anyone with the link can join' : 'Members need your approval to join'}</Text>

              <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>Plan Mode</Text>
              <View style={styles.toggleRow}>
                <TouchableOpacity testID="mode-individual" style={[styles.toggleBtn, cPlanMode === 'individual' && { backgroundColor: colors.primary + '20', borderColor: colors.primary }]} onPress={() => setCPlanMode('individual')}>
                  <Ionicons name="person-outline" size={16} color={cPlanMode === 'individual' ? colors.primary : colors.textSecondary} />
                  <Text style={[styles.toggleText, { color: cPlanMode === 'individual' ? colors.primary : colors.textSecondary }]}>Individual</Text>
                </TouchableOpacity>
                <TouchableOpacity testID="mode-shared" style={[styles.toggleBtn, cPlanMode === 'shared' && { backgroundColor: colors.primary + '20', borderColor: colors.primary }]} onPress={() => setCPlanMode('shared')}>
                  <Ionicons name="people-outline" size={16} color={cPlanMode === 'shared' ? colors.primary : colors.textSecondary} />
                  <Text style={[styles.toggleText, { color: cPlanMode === 'shared' ? colors.primary : colors.textSecondary }]}>Shared Plan</Text>
                </TouchableOpacity>
              </View>

              {cPlanMode === 'shared' && (
                <>
                  <Text style={[styles.fieldLabel, { color: colors.textSecondary }]}>Select Plan</Text>
                  {plans.map(plan => (
                    <TouchableOpacity key={plan.id} style={[styles.planOption, selectedPlan === plan.id && { backgroundColor: colors.primary + '15', borderColor: colors.primary }]} onPress={() => setSelectedPlan(plan.id)}>
                      <Text style={[styles.planOptionText, { color: selectedPlan === plan.id ? colors.primary : colors.textPrimary }]}>{plan.name}</Text>
                    </TouchableOpacity>
                  ))}
                </>
              )}
            </ScrollView>
            <TouchableOpacity testID="submit-create-circle" style={[styles.createBtn, { backgroundColor: colors.primary }]} onPress={handleCreate} disabled={creating}>
              {creating ? <ActivityIndicator color={colors.primaryForeground} /> : <Text style={[styles.createBtnText, { color: colors.primaryForeground }]}>Create Circle</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Join Circle Modal */}
      <Modal visible={showJoin} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={[styles.joinModal, { backgroundColor: colors.background, borderColor: colors.border }]}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.textPrimary }]}>Join a Circle</Text>
              <TouchableOpacity testID="close-join-modal" onPress={() => setShowJoin(false)}>
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>
            <Text style={[styles.joinHint, { color: colors.textSecondary }]}>Enter the invite code shared with you</Text>
            <TextInput testID="invite-code-input" style={[styles.codeInput, { backgroundColor: colors.muted, borderColor: colors.border, color: colors.textPrimary }]} placeholder="e.g., ABC12345" placeholderTextColor={colors.mutedForeground} value={joinCode} onChangeText={t => setJoinCode(t.toUpperCase())} autoCapitalize="characters" maxLength={8} />
            <TouchableOpacity testID="submit-join-circle" style={[styles.createBtn, { backgroundColor: colors.primary }]} onPress={handleJoin} disabled={joining}>
              {joining ? <ActivityIndicator color={colors.primaryForeground} /> : <Text style={[styles.createBtnText, { color: colors.primaryForeground }]}>Join Circle</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  screenTitle: { fontSize: 28, fontWeight: '700', paddingHorizontal: 20 },
  screenSub: { fontSize: 14, paddingHorizontal: 20, marginBottom: 16 },
  actionRow: { flexDirection: 'row', paddingHorizontal: 20, gap: 10, marginBottom: 20 },
  actionBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, paddingVertical: 14, borderRadius: 14 },
  actionBtnText: { fontSize: 14, fontWeight: '600' },
  emptyCard: { marginHorizontal: 20, borderRadius: 16, borderWidth: 1, padding: 40, alignItems: 'center', gap: 8 },
  emptyTitle: { fontSize: 18, fontWeight: '600' },
  emptyText: { fontSize: 13, textAlign: 'center' },
  circleCard: { marginHorizontal: 20, borderRadius: 16, borderWidth: 1, padding: 16, marginBottom: 12 },
  circleCardHeader: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  circleIcon: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
  circleInfo: { flex: 1 },
  circleName: { fontSize: 16, fontWeight: '600' },
  circleMetaRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 2 },
  circleMeta: { fontSize: 12 },
  circleDesc: { fontSize: 13, marginTop: 8, lineHeight: 18 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { borderTopLeftRadius: 24, borderTopRightRadius: 24, borderWidth: 1, maxHeight: '85%' },
  joinModal: { borderTopLeftRadius: 24, borderTopRightRadius: 24, borderWidth: 1, padding: 24 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingBottom: 10 },
  modalTitle: { fontSize: 20, fontWeight: '700' },
  modalScroll: { paddingHorizontal: 20, maxHeight: 400 },
  fieldLabel: { fontSize: 13, fontWeight: '500', marginTop: 14, marginBottom: 6 },
  fieldInput: { borderRadius: 12, borderWidth: 1, paddingHorizontal: 14, height: 48, fontSize: 15 },
  multiline: { height: 80, textAlignVertical: 'top', paddingTop: 12 },
  fieldHint: { fontSize: 11, marginTop: 4 },
  toggleRow: { flexDirection: 'row', gap: 8 },
  toggleBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, paddingVertical: 12, borderRadius: 12, borderWidth: 1, borderColor: 'transparent' },
  toggleText: { fontSize: 13, fontWeight: '500' },
  planOption: { padding: 12, borderRadius: 12, borderWidth: 1, borderColor: 'transparent', marginBottom: 6 },
  planOptionText: { fontSize: 14, fontWeight: '500' },
  createBtn: { height: 50, borderRadius: 25, justifyContent: 'center', alignItems: 'center', margin: 20 },
  createBtnText: { fontSize: 16, fontWeight: '600' },
  joinHint: { fontSize: 13, marginBottom: 16 },
  codeInput: { borderRadius: 12, borderWidth: 1, paddingHorizontal: 14, height: 56, fontSize: 24, fontWeight: '700', textAlign: 'center', letterSpacing: 4 },
});
