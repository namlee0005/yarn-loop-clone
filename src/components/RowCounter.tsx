import React, { useCallback, useRef, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import api from '../lib/api';

interface Counter {
  id: string;
  name: string;
  currentValue: number;
  maxValue: number | null;
}

interface Props {
  counter: Counter;
  onUpdate?: (updated: Counter) => void;
}

type Direction = 'increment' | 'decrement' | 'reset';

export default function RowCounter({ counter, onUpdate }: Props) {
  const [value, setValue] = useState(counter.currentValue);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Prevent rapid-fire taps from racing each other
  const pendingRef = useRef<Direction | null>(null);

  const mutate = useCallback(
    async (direction: Direction) => {
      if (busy) {
        pendingRef.current = direction;
        return;
      }

      const previous = value;
      const optimistic =
        direction === 'increment'
          ? value + 1
          : direction === 'decrement'
          ? Math.max(0, value - 1)
          : 0;

      // Optimistic update — paint immediately, reconcile after
      setValue(optimistic);
      setBusy(true);
      setError(null);

      try {
        const { data } = await api.patch<Counter>(
          `/counters/${counter.id}/${direction}`,
        );
        setValue(data.currentValue);
        onUpdate?.(data);
      } catch {
        // Rollback on failure
        setValue(previous);
        setError('Update failed. Try again.');
      } finally {
        setBusy(false);
        // Drain any tap queued while we were inflight
        if (pendingRef.current) {
          const next = pendingRef.current;
          pendingRef.current = null;
          mutate(next);
        }
      }
    },
    [busy, counter.id, onUpdate, value],
  );

  const progress =
    counter.maxValue && counter.maxValue > 0
      ? Math.min(value / counter.maxValue, 1)
      : null;

  return (
    <View style={styles.container}>
      <Text style={styles.name} numberOfLines={1}>
        {counter.name}
      </Text>

      {/* Progress bar */}
      {progress !== null && (
        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${progress * 100}%` as any }]} />
        </View>
      )}

      <View style={styles.controls}>
        <TouchableOpacity
          style={[styles.btn, styles.btnSecondary]}
          onPress={() => mutate('decrement')}
          disabled={busy || value === 0}
          activeOpacity={0.7}
        >
          <Text style={[styles.btnText, styles.btnTextSecondary]}>−</Text>
        </TouchableOpacity>

        <View style={styles.valueWrap}>
          {busy ? (
            <ActivityIndicator size="small" color="#6B46C1" />
          ) : (
            <Text style={styles.value}>{value}</Text>
          )}
          {counter.maxValue != null && (
            <Text style={styles.maxValue}>/ {counter.maxValue}</Text>
          )}
        </View>

        <TouchableOpacity
          style={[styles.btn, styles.btnPrimary]}
          onPress={() => mutate('increment')}
          disabled={busy || (counter.maxValue != null && value >= counter.maxValue)}
          activeOpacity={0.7}
        >
          <Text style={[styles.btnText, styles.btnTextPrimary]}>＋</Text>
        </TouchableOpacity>
      </View>

      {error && <Text style={styles.error}>{error}</Text>}

      <TouchableOpacity onPress={() => mutate('reset')} disabled={busy || value === 0}>
        <Text style={[styles.resetLink, (busy || value === 0) && styles.resetLinkDisabled]}>
          Reset
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    gap: 10,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  name: { fontSize: 15, fontWeight: '600', color: '#111827' },
  progressTrack: {
    height: 4,
    backgroundColor: '#E5E7EB',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6B46C1',
    borderRadius: 2,
  },
  controls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  btn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnPrimary: { backgroundColor: '#6B46C1' },
  btnSecondary: { backgroundColor: '#F3F4F6' },
  btnText: { fontSize: 24, lineHeight: 28, fontWeight: '500' },
  btnTextPrimary: { color: '#fff' },
  btnTextSecondary: { color: '#374151' },
  valueWrap: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 4,
    minWidth: 60,
    justifyContent: 'center',
  },
  value: { fontSize: 32, fontWeight: '700', color: '#111827' },
  maxValue: { fontSize: 14, color: '#9CA3AF' },
  error: { fontSize: 12, color: '#EF4444', textAlign: 'center' },
  resetLink: { fontSize: 13, color: '#6B46C1', textAlign: 'center' },
  resetLinkDisabled: { color: '#D1D5DB' },
});