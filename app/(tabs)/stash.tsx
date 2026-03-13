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

interface StashItem {
  id: string;
  yarnName: string;
  brand: string;
  colorway: string;
  weight: string;
  skeinCount: number;
  gramsPerSkein: number;
  colorHex: string | null;
}

const WEIGHT_LABELS: Record<string, string> = {
  lace: 'Lace',
  fingering: 'Fingering',
  sport: 'Sport',
  dk: 'DK',
  worsted: 'Worsted',
  bulky: 'Bulky',
  super_bulky: 'Super Bulky',
};

export default function StashScreen() {
  const [items, setItems] = useState<StashItem[]>([]);
  const [filtered, setFiltered] = useState<StashItem[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStash = useCallback(async () => {
    try {
      setError(null);
      const { data } = await api.get<StashItem[]>('/stash');
      setItems(data);
      setFiltered(data);
    } catch {
      setError('Failed to load stash. Pull down to retry.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchStash(); }, [fetchStash]);

  const onSearch = useCallback(
    (text: string) => {
      setQuery(text);
      const q = text.toLowerCase().trim();
      if (!q) {
        setFiltered(items);
        return;
      }
      setFiltered(
        items.filter(
          (i) =>
            i.yarnName.toLowerCase().includes(q) ||
            i.brand.toLowerCase().includes(q) ||
            i.colorway.toLowerCase().includes(q) ||
            i.weight.toLowerCase().includes(q),
        ),
      );
    },
    [items],
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchStash();
  }, [fetchStash]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6B46C1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Search bar */}
      <View style={styles.searchWrap}>
        <Ionicons name="search-outline" size={16} color="#9CA3AF" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search yarn, brand, colorway…"
          placeholderTextColor="#9CA3AF"
          value={query}
          onChangeText={onSearch}
          clearButtonMode="while-editing"
          returnKeyType="search"
          autoCapitalize="none"
          autoCorrect={false}
        />
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        contentContainerStyle={filtered.length === 0 ? styles.centered : styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={styles.emptyText}>
            {error ?? (query ? 'No results for that search.' : 'Your stash is empty. Add some yarn!')}
          </Text>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => router.push(`/stash/${item.id}`)}
            activeOpacity={0.75}
          >
            <View style={styles.cardLeft}>
              <View
                style={[
                  styles.colorSwatch,
                  { backgroundColor: item.colorHex ?? '#E5E7EB' },
                ]}
              />
              <View style={styles.cardBody}>
                <Text style={styles.yarnName} numberOfLines={1}>
                  {item.yarnName}
                </Text>
                <Text style={styles.brand}>{item.brand}</Text>
                <Text style={styles.colorway} numberOfLines={1}>
                  {item.colorway}
                </Text>
              </View>
            </View>
            <View style={styles.cardRight}>
              <View style={styles.weightBadge}>
                <Text style={styles.weightText}>
                  {WEIGHT_LABELS[item.weight] ?? item.weight}
                </Text>
              </View>
              <Text style={styles.skeinCount}>
                {item.skeinCount} skein{item.skeinCount !== 1 ? 's' : ''}
              </Text>
              <Text style={styles.grams}>{item.gramsPerSkein}g each</Text>
            </View>
          </TouchableOpacity>
        )}
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push('/stash/new')}
        activeOpacity={0.85}
      >
        <Text style={styles.fabText}>＋</Text>
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
  list: { padding: 16, paddingTop: 8, gap: 10 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  cardLeft: { flexDirection: 'row', flex: 1, gap: 12, alignItems: 'center' },
  colorSwatch: { width: 36, height: 36, borderRadius: 18 },
  cardBody: { flex: 1 },
  yarnName: { fontSize: 15, fontWeight: '600', color: '#111827' },
  brand: { fontSize: 12, color: '#6B7280', marginTop: 1 },
  colorway: { fontSize: 12, color: '#6B7280' },
  cardRight: { alignItems: 'flex-end', justifyContent: 'center', gap: 4 },
  weightBadge: {
    backgroundColor: '#EDE9FE',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  weightText: { fontSize: 11, color: '#6B46C1', fontWeight: '600' },
  skeinCount: { fontSize: 13, color: '#374151', fontWeight: '500' },
  grams: { fontSize: 11, color: '#9CA3AF' },
  emptyText: { color: '#9CA3AF', textAlign: 'center', fontSize: 15 },
  fab: {
    position: 'absolute', bottom: 24, right: 24,
    backgroundColor: '#6B46C1', width: 56, height: 56,
    borderRadius: 28, justifyContent: 'center', alignItems: 'center',
    shadowColor: '#6B46C1', shadowOpacity: 0.4, shadowRadius: 12, elevation: 6,
  },
  fabText: { color: '#fff', fontSize: 28, lineHeight: 32 },
});