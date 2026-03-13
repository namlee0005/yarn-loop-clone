import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import api from '../../src/lib/api';

interface Pattern {
  id: string;
  name: string;
  designer: string;
  category: string;
  difficulty: 'beginner' | 'easy' | 'intermediate' | 'advanced';
  yarnWeight: string;
  needleSize: string;
  thumbnailUrl: string | null;
  isFavorite: boolean;
}

const DIFFICULTY_COLOR: Record<Pattern['difficulty'], string> = {
  beginner: '#10B981',
  easy: '#3B82F6',
  intermediate: '#F59E0B',
  advanced: '#EF4444',
};

const CATEGORIES = ['All', 'Sweater', 'Shawl', 'Socks', 'Hat', 'Amigurumi', 'Other'];

export default function PatternsScreen() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [filtered, setFiltered] = useState<Pattern[]>([]);
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = useCallback(async () => {
    try {
      setError(null);
      const { data } = await api.get<Pattern[]>('/patterns');
      setPatterns(data);
      setFiltered(data);
    } catch {
      setError('Failed to load patterns. Pull down to retry.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchPatterns(); }, [fetchPatterns]);

  const applyFilters = useCallback(
    (q: string, category: string, source: Pattern[]) => {
      let result = source;
      if (category !== 'All') {
        result = result.filter((p) => p.category === category);
      }
      const lq = q.toLowerCase().trim();
      if (lq) {
        result = result.filter(
          (p) =>
            p.name.toLowerCase().includes(lq) ||
            p.designer.toLowerCase().includes(lq) ||
            p.yarnWeight.toLowerCase().includes(lq),
        );
      }
      return result;
    },
    [],
  );

  const onSearch = useCallback(
    (text: string) => {
      setQuery(text);
      setFiltered(applyFilters(text, activeCategory, patterns));
    },
    [activeCategory, applyFilters, patterns],
  );

  const onCategory = useCallback(
    (cat: string) => {
      setActiveCategory(cat);
      setFiltered(applyFilters(query, cat, patterns));
    },
    [applyFilters, patterns, query],
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchPatterns();
  }, [fetchPatterns]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6B46C1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Search */}
      <View style={styles.searchWrap}>
        <Ionicons name="search-outline" size={16} color="#9CA3AF" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search patterns, designers…"
          placeholderTextColor="#9CA3AF"
          value={query}
          onChangeText={onSearch}
          clearButtonMode="while-editing"
          returnKeyType="search"
          autoCapitalize="none"
          autoCorrect={false}
        />
      </View>

      {/* Category chips */}
      <FlatList
        horizontal
        data={CATEGORIES}
        keyExtractor={(c) => c}
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chips}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.chip, activeCategory === item && styles.chipActive]}
            onPress={() => onCategory(item)}
            activeOpacity={0.7}
          >
            <Text style={[styles.chipText, activeCategory === item && styles.chipTextActive]}>
              {item}
            </Text>
          </TouchableOpacity>
        )}
      />

      {/* Pattern list */}
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        contentContainerStyle={filtered.length === 0 ? styles.centered : styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={styles.emptyText}>
            {error ?? (query || activeCategory !== 'All'
              ? 'No patterns match those filters.'
              : 'No patterns yet. Import your first one!')}
          </Text>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/patterns/${item.id}`)}
            activeOpacity={0.75}
          >
            {/* Thumbnail placeholder */}
            <View style={styles.thumbnail}>
              <Ionicons name="document-text-outline" size={28} color="#C4B5FD" />
            </View>

            <View style={styles.cardBody}>
              <View style={styles.cardHeader}>
                <Text style={styles.patternName} numberOfLines={1}>
                  {item.name}
                </Text>
                {item.isFavorite && (
                  <Ionicons name="heart" size={14} color="#EF4444" />
                )}
              </View>
              <Text style={styles.designer}>{item.designer}</Text>
              <View style={styles.cardMeta}>
                <View
                  style={[
                    styles.diffBadge,
                    { backgroundColor: DIFFICULTY_COLOR[item.difficulty] + '20' },
                  ]}
                >
                  <Text
                    style={[
                      styles.diffText,
                      { color: DIFFICULTY_COLOR[item.difficulty] },
                    ]}
                  >
                    {item.difficulty}
                  </Text>
                </View>
                <Text style={styles.meta}>
                  {item.yarnWeight} · {item.needleSize}
                </Text>
              </View>
            </View>
          </TouchableOpacity>
        )}
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push('/patterns/import')}
        activeOpacity={0.85}
      >
        <Ionicons name="cloud-upload-outline" size={24} color="#fff" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  searchWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    margin: 16,
    marginBottom: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: 12,
    height: 44,
  },
  searchIcon: { marginRight: 8 },
  searchInput: { flex: 1, fontSize: 15, color: '#111827' },
  chips: { paddingHorizontal: 16, paddingBottom: 10, gap: 8 },
  chip: {
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 6,
    backgroundColor: '#F3F4F6',
  },
  chipActive: { backgroundColor: '#6B46C1' },
  chipText: { fontSize: 13, color: '#6B7280', fontWeight: '500' },
  chipTextActive: { color: '#fff' },
  list: { padding: 16, paddingTop: 4, gap: 10 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    gap: 12,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  thumbnail: {
    width: 56,
    height: 56,
    borderRadius: 8,
    backgroundColor: '#F5F3FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardBody: { flex: 1 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  patternName: { fontSize: 15, fontWeight: '600', color: '#111827', flex: 1 },
  designer: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  cardMeta: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 6 },
  diffBadge: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2 },
  diffText: { fontSize: 11, fontWeight: '600', textTransform: 'capitalize' },
  meta: { fontSize: 12, color: '#9CA3AF' },
  emptyText: { color: '#9CA3AF', textAlign: 'center', fontSize: 15 },
  fab: {
    position: 'absolute', bottom: 24, right: 24,
    backgroundColor: '#6B46C1', width: 56, height: 56,
    borderRadius: 28, justifyContent: 'center', alignItems: 'center',
    shadowColor: '#6B46C1', shadowOpacity: 0.4, shadowRadius: 12, elevation: 6,
  },
});