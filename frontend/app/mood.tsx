import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../src/ThemeContext';
import { api } from '../src/api';

const MOOD_ICONS: Record<string, string> = {
  'cloud-rain': 'rainy', sun: 'sunny', heart: 'heart', gift: 'gift', compass: 'compass', users: 'people',
};

export default function MoodScreen() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [moods, setMoods] = useState<any>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMoodSuggestions().then(data => { setMoods(data.moods); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]} contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 40 }}>
      {/* Header */}
      <View style={styles.headerRow}>
        <TouchableOpacity testID="mood-back-btn" onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={22} color={colors.textPrimary} />
        </TouchableOpacity>
        <Text style={[styles.title, { color: colors.textPrimary }]}>How are you feeling?</Text>
      </View>
      <Text style={[styles.subtitle, { color: colors.textSecondary }]}>Select your mood for personalized Bible passages</Text>

      {/* Mood Cards */}
      <View style={styles.moodGrid}>
        {moods && Object.entries(moods).map(([key, mood]: [string, any]) => {
          const isSelected = selected === key;
          const iconName = MOOD_ICONS[mood.icon] || 'help-circle';
          return (
            <TouchableOpacity
              key={key}
              testID={`mood-card-${key}`}
              style={[styles.moodCard, { backgroundColor: isSelected ? mood.color + '25' : colors.surface, borderColor: isSelected ? mood.color : colors.border }]}
              onPress={() => setSelected(key)}
            >
              <View style={[styles.moodIcon, { backgroundColor: mood.color + '20' }]}>
                <Ionicons name={iconName as any} size={24} color={mood.color} />
              </View>
              <Text style={[styles.moodLabel, { color: colors.textPrimary }]}>{mood.label}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Passages */}
      {selected && moods[selected] && (
        <View style={styles.passagesSection}>
          <Text style={[styles.passagesTitle, { color: colors.textPrimary }]}>Suggested Passages</Text>
          {moods[selected].passages.map((p: any, i: number) => (
            <TouchableOpacity
              key={i}
              testID={`mood-passage-${i}`}
              style={[styles.passageCard, { backgroundColor: colors.surface, borderColor: colors.border }]}
              onPress={() => router.push({ pathname: '/reader', params: { bookSlug: p.book_slug, chapter: p.chapter, version: 'kjv' } })}
            >
              <View style={{ flex: 1 }}>
                <Text style={[styles.passageRef, { color: colors.primary }]}>{p.ref}</Text>
                <Text style={[styles.passageTitle, { color: colors.textSecondary }]}>{p.title}</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color={colors.mutedForeground} />
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 20, marginBottom: 8 },
  title: { fontSize: 24, fontWeight: '700' },
  subtitle: { fontSize: 14, paddingHorizontal: 20, marginBottom: 24 },
  moodGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 16, gap: 12, marginBottom: 24 },
  moodCard: { width: '45%', borderRadius: 16, padding: 20, borderWidth: 1.5, alignItems: 'center', gap: 10 },
  moodIcon: { width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center' },
  moodLabel: { fontSize: 15, fontWeight: '600' },
  passagesSection: { paddingHorizontal: 20 },
  passagesTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  passageCard: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 14, borderWidth: 1, marginBottom: 8, gap: 12 },
  passageRef: { fontSize: 15, fontWeight: '600' },
  passageTitle: { fontSize: 12, marginTop: 2 },
});
