import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from 'react-native-reanimated';

import { colors, motion, radius, spacing, type } from '../design/tokens';
import { STYLES, type StyleId } from '../models/types';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

interface Props {
  selected: StyleId;
  disabled?: boolean;
  onSelect: (style: StyleId) => void;
}

export function StyleSelector({ selected, disabled, onSelect }: Props) {
  return (
    <View style={styles.row}>
      {STYLES.map((s) => {
        const active = s.id === selected;
        return (
          <StyleChip
            key={s.id}
            label={s.label}
            blurb={s.blurb}
            active={active}
            disabled={disabled}
            onPress={() => onSelect(s.id)}
          />
        );
      })}
    </View>
  );
}

function StyleChip({
  label,
  blurb,
  active,
  disabled,
  onPress,
}: {
  label: string;
  blurb: string;
  active: boolean;
  disabled?: boolean;
  onPress: () => void;
}) {
  const scale = useSharedValue(1);
  const anim = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
  return (
    <AnimatedPressable
      disabled={disabled}
      onPress={onPress}
      onPressIn={() => {
        scale.value = withSpring(0.95, motion.press);
      }}
      onPressOut={() => {
        scale.value = withSpring(1, motion.spring);
      }}
      style={[styles.chip, active && styles.chipActive, disabled && { opacity: 0.5 }, anim]}
    >
      <Text style={[styles.label, active && styles.labelActive]}>{label}</Text>
      <Text style={[styles.blurb, active && styles.blurbActive]}>{blurb}</Text>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    justifyContent: 'center',
  },
  chip: {
    minWidth: '46%',
    flexGrow: 1,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.styleChip,
  },
  chipActive: {
    backgroundColor: colors.styleChipActive,
  },
  label: {
    ...type.button,
    color: colors.ink,
  },
  labelActive: {
    color: '#FFF',
  },
  blurb: {
    ...type.caption,
    color: colors.muted,
    marginTop: 2,
  },
  blurbActive: {
    color: 'rgba(255,255,255,0.75)',
  },
});
