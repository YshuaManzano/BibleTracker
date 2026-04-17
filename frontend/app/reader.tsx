import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, TextInput, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../src/ThemeContext';
import { api } from '../src/api';

export default function ReaderScreen() {
  const { colors } = useTheme();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const params = useLocalSearchParams<{ bookSlug: string; chapter: string; planId?: string; version?: string }>();
  const bookSlug = params.bookSlug || 'genesis';
  const chapter = parseInt(params.chapter || '1', 10);
  const planId = params.planId || '';
  const version = params.version || 'kjv';

  const [chapterData, setChapterData] = useState<any>(null);
  const [summary, setSummary] = useState('');
  const [notes, setNotes] = useState<any[]>([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [marking, setMarking] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [ch, n] = await Promise.all([
        api.getChapter(version, bookSlug, chapter),
        api.getNotes(bookSlug, chapter),
      ]);
      setChapterData(ch);
      setNotes(n.notes || []);
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally { setLoading(false); }
  }, [bookSlug, chapter, version]);

  useEffect(() => { loadData(); }, [loadData]);

  async function loadSummary() {
    setSummaryLoading(true);
    setShowSummary(true);
    try {
      const data = await api.getSummary(bookSlug, chapter);
      setSummary(data.summary || '');
    } catch { setSummary('Unable to load summary.'); }
    finally { setSummaryLoading(false); }
  }

  async function handleMarkRead() {
    if (!planId) {
      // Just mark without plan
      Alert.alert('Info', 'Start a reading plan to track your progress!');
      return;
    }
    setMarking(true);
    try {
      await api.markRead(planId, bookSlug, chapter);
      Alert.alert('Done!', `${chapterData?.book || bookSlug} ${chapter} marked as read.`);
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally { setMarking(false); }
  }

  async function handleAddNote() {
    if (!newNote.trim()) return;
    try {
      const note = await api.createNote(bookSlug, chapter, newNote.trim());
      setNotes([note, ...notes]);
      setNewNote('');
    } catch (e: any) { Alert.alert('Error', e.message); }
  }

  async function handleDeleteNote(noteId: string) {
    try {
      await api.deleteNote(noteId);
      setNotes(notes.filter(n => n.id !== noteId));
    } catch (e: any) { Alert.alert('Error', e.message); }
  }

  if (loading) return (
    <View style={[styles.center, { backgroundColor: colors.background, paddingTop: insets.top }]}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.background }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      {/* Header */}
      <View style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.surface, borderBottomColor: colors.border }]}>
        <TouchableOpacity testID="reader-back-btn" onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={[styles.headerTitle, { color: colors.textPrimary }]}>{chapterData?.book || bookSlug}</Text>
          <Text style={[styles.headerSub, { color: colors.textSecondary }]}>Chapter {chapter} • {version.toUpperCase()}</Text>
        </View>
        <TouchableOpacity testID="reader-notes-btn" onPress={() => setShowNotes(!showNotes)} style={styles.iconBtn}>
          <Ionicons name="create-outline" size={20} color={showNotes ? colors.primary : colors.textSecondary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
        {/* AI Summary */}
        <View style={styles.summarySection}>
          {!showSummary ? (
            <TouchableOpacity testID="load-summary-btn" style={[styles.summaryBtn, { backgroundColor: colors.muted, borderColor: colors.border }]} onPress={loadSummary}>
              <Ionicons name="bulb-outline" size={18} color={colors.accent} />
              <Text style={[styles.summaryBtnText, { color: colors.textPrimary }]}>TL;DR Summary</Text>
              <Ionicons name="chevron-forward" size={14} color={colors.mutedForeground} />
            </TouchableOpacity>
          ) : (
            <View style={[styles.summaryBox, { backgroundColor: colors.accent + '10', borderColor: colors.accent + '30' }]}>
              <View style={styles.summaryHeader}>
                <Ionicons name="bulb" size={16} color={colors.accent} />
                <Text style={[styles.summaryLabel, { color: colors.accent }]}>AI Summary</Text>
                <TouchableOpacity onPress={() => setShowSummary(false)}>
                  <Ionicons name="close" size={16} color={colors.textSecondary} />
                </TouchableOpacity>
              </View>
              {summaryLoading ? <ActivityIndicator color={colors.accent} /> :
                <Text testID="reader-summary-text" style={[styles.summaryText, { color: colors.textPrimary }]}>{summary}</Text>}
            </View>
          )}
        </View>

        {/* Bible Text */}
        <View testID="reader-content" style={styles.textContainer}>
          {(chapterData?.verses || []).map((v: any, i: number) => (
            <Text key={i} style={[styles.verseText, { color: colors.textPrimary }]}>
              <Text style={[styles.verseNum, { color: colors.primary }]}>{v.verse || i + 1} </Text>
              {v.text}{'  '}
            </Text>
          ))}
          {(!chapterData?.verses || chapterData.verses.length === 0) && chapterData?.text && (
            <Text style={[styles.verseText, { color: colors.textPrimary }]}>{chapterData.text}</Text>
          )}
        </View>

        {/* Notes Section */}
        {showNotes && (
          <View style={[styles.notesSection, { borderTopColor: colors.border }]}>
            <Text style={[styles.notesTitle, { color: colors.textPrimary }]}>Notes</Text>
            <View style={[styles.noteInputRow, { backgroundColor: colors.muted, borderColor: colors.border }]}>
              <TextInput
                testID="note-input"
                style={[styles.noteInput, { color: colors.textPrimary }]}
                placeholder="Add a note or prayer..."
                placeholderTextColor={colors.mutedForeground}
                value={newNote}
                onChangeText={setNewNote}
                multiline
              />
              <TouchableOpacity testID="save-note-btn" onPress={handleAddNote} style={[styles.noteSendBtn, { backgroundColor: colors.primary }]}>
                <Ionicons name="send" size={16} color={colors.primaryForeground} />
              </TouchableOpacity>
            </View>
            {notes.map(note => (
              <View key={note.id} style={[styles.noteCard, { backgroundColor: colors.muted, borderColor: colors.border }]}>
                <Text style={[styles.noteText, { color: colors.textPrimary }]}>{note.text}</Text>
                <View style={styles.noteFooter}>
                  <Text style={[styles.noteDate, { color: colors.mutedForeground }]}>{new Date(note.created_at).toLocaleDateString()}</Text>
                  <TouchableOpacity testID={`delete-note-${note.id}`} onPress={() => handleDeleteNote(note.id)}>
                    <Ionicons name="trash-outline" size={14} color={colors.danger} />
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Bottom Bar */}
      <View style={[styles.bottomBar, { backgroundColor: colors.surface, borderTopColor: colors.border, paddingBottom: insets.bottom + 8 }]}>
        <TouchableOpacity testID="mark-read-btn" style={[styles.markReadBtn, { backgroundColor: colors.primary }]} onPress={handleMarkRead} disabled={marking}>
          {marking ? <ActivityIndicator color={colors.primaryForeground} /> : (
            <>
              <Ionicons name="checkmark-circle" size={20} color={colors.primaryForeground} />
              <Text style={[styles.markReadText, { color: colors.primaryForeground }]}>Mark as Read</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingBottom: 12, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerCenter: { flex: 1, marginLeft: 4 },
  headerTitle: { fontSize: 18, fontWeight: '600' },
  headerSub: { fontSize: 12 },
  iconBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  scrollContainer: { flex: 1 },
  scrollContent: { padding: 20, paddingBottom: 40 },
  summarySection: { marginBottom: 20 },
  summaryBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 14, borderRadius: 12, borderWidth: 1 },
  summaryBtnText: { flex: 1, fontSize: 14, fontWeight: '500' },
  summaryBox: { padding: 16, borderRadius: 12, borderWidth: 1 },
  summaryHeader: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 },
  summaryLabel: { flex: 1, fontSize: 12, fontWeight: '700', letterSpacing: 0.5 },
  summaryText: { fontSize: 14, lineHeight: 22 },
  textContainer: { marginBottom: 20 },
  verseText: { fontSize: 17, lineHeight: 30, fontFamily: 'serif', marginBottom: 2 },
  verseNum: { fontSize: 12, fontWeight: '700', fontFamily: 'serif' },
  notesSection: { borderTopWidth: 1, paddingTop: 20 },
  notesTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  noteInputRow: { flexDirection: 'row', alignItems: 'flex-end', borderRadius: 14, borderWidth: 1, padding: 8, marginBottom: 12, gap: 8 },
  noteInput: { flex: 1, fontSize: 14, maxHeight: 100, minHeight: 40, paddingHorizontal: 8 },
  noteSendBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  noteCard: { padding: 14, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
  noteText: { fontSize: 14, lineHeight: 20 },
  noteFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 },
  noteDate: { fontSize: 11 },
  bottomBar: { flexDirection: 'row', paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1 },
  markReadBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, height: 48, borderRadius: 24 },
  markReadText: { fontSize: 15, fontWeight: '600' },
});
