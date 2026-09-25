import * as Sharing from 'expo-sharing';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { SoftButton } from '../components/SoftButton';
import { StyleSelector } from '../components/StyleSelector';
import { ErrorBanner, UnsavedDialog } from '../components/Feedback';
import { track } from '../analytics/events';
import { colors, spacing, type } from '../design/tokens';
import { useApp } from '../state/AppContext';
import { usage } from '../usage/entitlement';

export default function ResultScreen() {
  const app = useApp();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [confirmNew, setConfirmNew] = useState(false);

  useEffect(() => {
    if (app.phase === 'generating') router.replace('/generating');
    if (app.phase === 'canvas' && !app.activeAsset) router.replace('/');
  }, [app.phase, app.activeAsset, router]);

  const uri = app.activeAsset?.imageUri;

  const onShare = async () => {
    if (!uri) return;
    usage.record('share');
    track('shared', { style: app.creation.style });
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(uri);
    }
  };

  return (
    <View style={[styles.root, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Text style={styles.brand}>Dooji</Text>
        <Pressable onPress={() => router.push('/library')} style={styles.link}>
          <Text style={styles.linkText}>Library</Text>
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingBottom: Math.max(insets.bottom, spacing.lg) + spacing.md },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View entering={FadeIn.duration(400)} style={styles.hero}>
          {uri ? (
            <Image source={{ uri }} style={styles.image} resizeMode="contain" />
          ) : (
            <Text style={styles.missing}>No image yet</Text>
          )}
        </Animated.View>

        <Animated.View entering={FadeInDown.delay(80).springify()} style={styles.block}>
          <Text style={styles.sectionLabel}>Style</Text>
          <StyleSelector
            selected={app.creation.style}
            onSelect={(style) => void app.selectStyle(style)}
          />
        </Animated.View>

        {app.lastError ? (
          <ErrorBanner
            message={app.lastError}
            onRetry={() => void app.retryTransform()}
            onEdit={() => {
              app.editDoodle();
              router.replace('/');
            }}
          />
        ) : null}

        <Animated.View entering={FadeInDown.delay(140).springify()} style={styles.actions}>
          <SoftButton
            label="Edit doodle"
            variant="secondary"
            onPress={() => {
              app.editDoodle();
              router.replace('/');
            }}
          />
          <SoftButton
            label="Try another"
            variant="ghost"
            onPress={() => void app.tryAnother()}
          />
          <SoftButton label="Save" onPress={() => void app.saveCreation()} />
          <SoftButton label="Share" variant="secondary" onPress={() => void onShare()} />
          <SoftButton
            label="New doodle"
            variant="ghost"
            onPress={() => setConfirmNew(true)}
          />
        </Animated.View>
      </ScrollView>

      <UnsavedDialog
        visible={confirmNew}
        dirty={app.dirty || !app.creation.saved}
        onSave={async () => {
          await app.saveCreation();
          setConfirmNew(false);
          app.newDoodle();
          router.replace('/');
        }}
        onDiscard={() => {
          setConfirmNew(false);
          app.newDoodle();
          router.replace('/');
        }}
        onCancel={() => setConfirmNew(false)}
      />
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
  brand: { ...type.brand, color: colors.brand },
  link: {
    minHeight: 40,
    paddingHorizontal: spacing.md,
    justifyContent: 'center',
    backgroundColor: colors.accentSoft,
    borderRadius: 12,
  },
  linkText: { ...type.caption, color: colors.ink, fontFamily: 'Fredoka_500Medium' },
  content: {
    paddingHorizontal: spacing.lg,
    gap: spacing.xl,
  },
  hero: {
    minHeight: 320,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  image: {
    width: '100%',
    height: 360,
  },
  missing: { ...type.body, color: colors.muted },
  block: { gap: spacing.md },
  sectionLabel: {
    ...type.caption,
    color: colors.muted,
    textAlign: 'center',
  },
  actions: { gap: spacing.sm },
});
