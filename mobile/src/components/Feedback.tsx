import React, { useEffect } from 'react';
import { Modal, StyleSheet, Text, View } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withSequence,
  withSpring,
} from 'react-native-reanimated';

import { colors, motion, radius, spacing, type } from '../design/tokens';
import { SoftButton } from './SoftButton';

interface Props {
  visible: boolean;
  dirty: boolean;
  onSave: () => void;
  onDiscard: () => void;
  onCancel: () => void;
}

export function UnsavedDialog({ visible, dirty, onSave, onDiscard, onCancel }: Props) {
  if (!visible) return null;
  return (
    <Modal transparent animationType="fade" visible={visible} onRequestClose={onCancel}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>
            {dirty ? 'Save this doodle?' : 'Start fresh?'}
          </Text>
          <Text style={styles.body}>
            {dirty
              ? 'You have an unsaved creation. Save it to your library, discard it, or cancel.'
              : 'Ready for a new doodle.'}
          </Text>
          <View style={styles.actions}>
            {dirty && <SoftButton label="Save" onPress={onSave} />}
            <SoftButton label="Discard" variant="danger" onPress={onDiscard} />
            <SoftButton label="Cancel" variant="ghost" onPress={onCancel} />
          </View>
        </View>
      </View>
    </Modal>
  );
}

interface GenProps {
  copy: string;
}

export function GeneratingView({ copy }: GenProps) {
  const pulse = useSharedValue(0.92);
  useEffect(() => {
    pulse.value = withRepeat(
      withSequence(
        withSpring(1, motion.soft),
        withSpring(0.92, motion.soft),
      ),
      -1,
      false,
    );
  }, [pulse]);
  const anim = useAnimatedStyle(() => ({ transform: [{ scale: pulse.value }] }));

  return (
    <View style={styles.genWrap}>
      <Animated.View style={[styles.orb, anim]} />
      <Text style={styles.genCopy}>{copy}</Text>
    </View>
  );
}

interface ErrProps {
  message: string;
  onRetry: () => void;
  onEdit: () => void;
}

export function ErrorBanner({ message, onRetry, onEdit }: ErrProps) {
  return (
    <View style={styles.err}>
      <Text style={styles.errText}>{message}</Text>
      <View style={styles.errActions}>
        <SoftButton label="Retry" onPress={onRetry} style={{ flex: 1 }} />
        <SoftButton label="Edit" variant="secondary" onPress={onEdit} style={{ flex: 1 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'center',
    padding: spacing.xl,
  },
  card: {
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.xl,
    padding: spacing.xl,
    gap: spacing.md,
  },
  title: {
    ...type.title,
    color: colors.brand,
  },
  body: {
    ...type.body,
    color: colors.muted,
  },
  actions: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  genWrap: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    gap: spacing.xl,
  },
  orb: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: colors.accentSoft,
    borderWidth: 3,
    borderColor: colors.accent,
  },
  genCopy: {
    ...type.title,
    color: colors.ink,
    textAlign: 'center',
    paddingHorizontal: spacing.xl,
  },
  err: {
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: radius.lg,
    backgroundColor: colors.dangerSoft,
    gap: spacing.md,
  },
  errText: {
    ...type.body,
    color: colors.ink,
    textAlign: 'center',
  },
  errActions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
});
