import { useRouter } from 'expo-router';
import React from 'react';
import {
  FlatList,
  Image,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { SoftButton } from '../components/SoftButton';
import { colors, radius, spacing, type } from '../design/tokens';
import { latestAsset, type Creation } from '../models/types';
import { useApp } from '../state/AppContext';

export default function LibraryScreen() {
  const app = useApp();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const open = (c: Creation) => {
    app.openCreation(c.id);
    router.replace(c.assets.length ? '/result' : '/');
  };

  return (
    <View style={[styles.root, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Text style={styles.title}>Library</Text>
        <SoftButton
          label="Canvas"
          variant="secondary"
          onPress={() => router.replace('/')}
          style={{ minHeight: 40, paddingHorizontal: spacing.md }}
        />
      </View>
      {app.library.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyTitle}>Nothing saved yet.</Text>
          <Text style={styles.emptyBody}>Your creations will land here.</Text>
          <SoftButton label="Start doodling" onPress={() => router.replace('/')} />
        </View>
      ) : (
        <FlatList
          data={app.library}
          keyExtractor={(item) => item.id}
          numColumns={2}
          contentContainerStyle={{
            padding: spacing.md,
            paddingBottom: Math.max(insets.bottom, spacing.lg),
            gap: spacing.md,
          }}
          columnWrapperStyle={{ gap: spacing.md }}
          renderItem={({ item }) => {
            const asset = latestAsset(item);
            return (
              <Pressable style={styles.card} onPress={() => open(item)}>
                {asset ? (
                  <Image source={{ uri: asset.imageUri }} style={styles.thumb} />
                ) : (
                  <View style={[styles.thumb, styles.thumbEmpty]}>
                    <Text style={styles.thumbHint}>Doodle</Text>
                  </View>
                )}
                <Text style={styles.meta} numberOfLines={1}>
                  {item.style} · {new Date(item.updatedAt).toLocaleDateString()}
                </Text>
              </Pressable>
            );
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
  header: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: { ...type.title, color: colors.brand },
  empty: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.md,
    padding: spacing.xl,
  },
  emptyTitle: { ...type.title, color: colors.ink },
  emptyBody: { ...type.body, color: colors.muted, marginBottom: spacing.md },
  card: {
    flex: 1,
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.border,
  },
  thumb: {
    width: '100%',
    aspectRatio: 1,
    backgroundColor: colors.canvas,
  },
  thumbEmpty: { alignItems: 'center', justifyContent: 'center' },
  thumbHint: { ...type.caption, color: colors.hint },
  meta: {
    ...type.caption,
    color: colors.muted,
    padding: spacing.sm,
  },
});
