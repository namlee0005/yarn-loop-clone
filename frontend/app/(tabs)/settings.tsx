import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function SettingsScreen() {
  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <Text style={styles.placeholder}>App settings and preferences.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  placeholder: { textAlign: 'center', marginTop: 40, color: '#9CA3AF' },
});