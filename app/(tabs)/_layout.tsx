import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

type IconName = React.ComponentProps<typeof Ionicons>['name'];

const TAB_CONFIG: {
  name: string;
  label: string;
  icon: IconName;
  activeIcon: IconName;
}[] = [
  { name: 'projects',  label: 'Projects',  icon: 'folder-outline',   activeIcon: 'folder'        },
  { name: 'stash',     label: 'Stash',     icon: 'layers-outline',   activeIcon: 'layers'        },
  { name: 'patterns',  label: 'Patterns',  icon: 'grid-outline',     activeIcon: 'grid'          },
  { name: 'settings',  label: 'Settings',  icon: 'settings-outline', activeIcon: 'settings'      },
];

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#6B46C1',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          borderTopWidth: 1,
          borderTopColor: '#E5E7EB',
          backgroundColor: '#fff',
          // Ensure sufficient height on devices without a safe-area notch
          paddingBottom: 4,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '500',
        },
        headerShown: true,
        headerStyle: { backgroundColor: '#fff' },
        headerTintColor: '#111827',
        headerTitleStyle: { fontWeight: '600', fontSize: 17 },
        headerShadowVisible: false,
      }}
    >
      {TAB_CONFIG.map(({ name, label, icon, activeIcon }) => (
        <Tabs.Screen
          key={name}
          name={name}
          options={{
            title: label,
            tabBarIcon: ({ focused, color, size }) => (
              <Ionicons
                name={focused ? activeIcon : icon}
                size={size}
                color={color}
              />
            ),
          }}
        />
      ))}
    </Tabs>
  );
}