import React from 'react';
import { Pressable, StyleSheet, Text, type ViewStyle } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from 'react-native-reanimated';

import { colors, motion, radius, spacing, type } from '../design/tokens';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

interface Props {
  label: string;
  onPress?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  disabled?: boolean;
  style?: ViewStyle;
  accessibilityLabel?: string;
}

export function SoftButton({
  label,
  onPress,
  variant = 'primary',
  disabled,
  style,
  accessibilityLabel,
}: Props) {
  const scale = useSharedValue(1);
  const anim = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  const bg =
    variant === 'primary'
      ? colors.accent
      : variant === 'secondary'
        ? colors.accentSoft
        : variant === 'danger'
          ? colors.dangerSoft
          : 'transparent';
  const fg =
    variant === 'primary'
      ? '#FFF'
      : variant === 'danger'
        ? colors.accent
        : colors.ink;

  return (
    <AnimatedPressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || label}
      disabled={disabled}
      onPress={onPress}
      onPressIn={() => {
        scale.value = withSpring(0.96, motion.press);
      }}
      onPressOut={() => {
        scale.value = withSpring(1, motion.press);
      }}
      style={[
        styles.base,
        { backgroundColor: bg, opacity: disabled ? 0.4 : 1 },
        variant === 'ghost' && styles.ghost,
        anim,
        style,
      ]}
    >
      <Text style={[styles.label, { color: fg }]}>{label}</Text>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: spacing.touch,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ghost: {
    borderWidth: 1,
    borderColor: colors.border,
  },
  label: {
    ...type.button,
  },
});
