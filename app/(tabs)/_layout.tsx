import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

type IconName = React.ComponentProps<typeof Ionicons>['name'];

const TAB_CONFIG: { name: string; label: string; icon: IconName; activeIcon: IconName }[] = [
  { name: 'projects', label: 'Projects', icon: 'folder-outline', activeIcon: 'folder' },
  { name: 'patterns', label: 'Patterns', icon: 'grid-outline', activeIcon: 'grid' },
  { name: 'settings', label: 'Settings', icon: 'settings-outline', activeIcon: 'settings' },
];

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#6B4E9B',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: { borderTopWidth: 1, borderTopColor: '#E5E7EB' },
        headerShown: true,
      }}
    >
      {TAB_CONFIG.map(({ name, label, icon, activeIcon }) => (
        <Tabs.Screen
          key={name}
          name={name}
          options={{
            title: label,
            tabBarIcon: ({ focused, color, size }) => (
              <Ionicons name={focused ? activeIcon : icon} size={size} color={color} />
            ),
          }}
        />
      ))}
    </Tabs>
  );
}