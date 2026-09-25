import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from 'react-native-reanimated';

import { colors, motion, radius, spacing, type } from '../design/tokens';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

interface Props {
  tool: 'brush' | 'eraser';
  color: string;
  size: number;
  colors: string[];
  canUndo: boolean;
  canRedo: boolean;
  hasStrokes: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onTool: (t: 'brush' | 'eraser') => void;
  onColor: (c: string) => void;
  onSize: (n: number) => void;
  onClear: () => void;
  onMakeIt: () => void;
}

function ToolChip({
  label,
  active,
  onPress,
  disabled,
}: {
  label: string;
  active?: boolean;
  onPress: () => void;
  disabled?: boolean;
}) {
  const scale = useSharedValue(1);
  const anim = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
  return (
    <AnimatedPressable
      disabled={disabled}
      onPress={onPress}
      onPressIn={() => {
        scale.value = withSpring(0.94, motion.press);
      }}
      onPressOut={() => {
        scale.value = withSpring(1, motion.press);
      }}
      style={[
        styles.chip,
        active && styles.chipActive,
        disabled && { opacity: 0.35 },
        anim,
      ]}
    >
      <Text style={[styles.chipText, active && styles.chipTextActive]}>{label}</Text>
    </AnimatedPressable>
  );
}

export function CanvasToolbar(props: Props) {
  return (
    <View style={styles.bar}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.row}
      >
        <ToolChip label="Undo" onPress={props.onUndo} disabled={!props.canUndo} />
        <ToolChip label="Redo" onPress={props.onRedo} disabled={!props.canRedo} />
        <ToolChip
          label="Brush"
          active={props.tool === 'brush'}
          onPress={() => props.onTool('brush')}
        />
        <ToolChip
          label="Eraser"
          active={props.tool === 'eraser'}
          onPress={() => props.onTool('eraser')}
        />
        <ToolChip label="Clear" onPress={props.onClear} disabled={!props.hasStrokes} />
        {[6, 10, 16].map((n) => (
          <ToolChip
            key={n}
            label={`${n}`}
            active={props.size === n}
            onPress={() => props.onSize(n)}
          />
        ))}
        {props.colors.map((c) => (
          <Pressable
            key={c}
            onPress={() => props.onColor(c)}
            style={[
              styles.swatch,
              { backgroundColor: c },
              props.color === c && styles.swatchActive,
              c === '#FFFFFF' && styles.swatchBorder,
            ]}
          />
        ))}
      </ScrollView>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Make it"
        disabled={!props.hasStrokes}
        onPress={props.onMakeIt}
        style={[styles.makeIt, !props.hasStrokes && { opacity: 0.4 }]}
      >
        <Text style={styles.makeItText}>Make it ✨</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  row: {
    alignItems: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.xs,
  },
  chip: {
    minHeight: 40,
    paddingHorizontal: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.styleChip,
    justifyContent: 'center',
  },
  chipActive: {
    backgroundColor: colors.styleChipActive,
  },
  chipText: {
    ...type.caption,
    color: colors.ink,
  },
  chipTextActive: {
    color: '#FFF',
  },
  swatch: {
    width: 32,
    height: 32,
    borderRadius: 16,
  },
  swatchActive: {
    borderWidth: 2,
    borderColor: colors.accent,
  },
  swatchBorder: {
    borderWidth: 1,
    borderColor: colors.border,
  },
  makeIt: {
    minHeight: spacing.touch,
    borderRadius: radius.lg,
    backgroundColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  makeItText: {
    ...type.button,
    color: '#FFF',
    fontSize: 18,
  },
});
