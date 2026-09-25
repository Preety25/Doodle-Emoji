/**
 * Lightweight design tokens — playful / premium / simple / magical.
 * Soft surfaces, restrained motion; canvas + generated object are the heroes.
 */

export const colors = {
  brand: '#1A1423',
  ink: '#2B2438',
  muted: '#7A708A',
  hint: '#9A90A4',
  surface: '#FFF8F4',
  surfaceElevated: '#FFFFFF',
  canvas: '#FFFCF9',
  accent: '#FF5C7A',
  accentSoft: '#FFE0E7',
  accentPressed: '#E54866',
  border: 'rgba(42, 36, 56, 0.08)',
  overlay: 'rgba(26, 20, 35, 0.45)',
  dangerSoft: '#FFF0F2',
  styleChip: '#F3EDF7',
  styleChipActive: '#1A1423',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  toolbar: 72,
  touch: 48,
} as const;

export const radius = {
  sm: 10,
  md: 16,
  lg: 22,
  xl: 28,
  pill: 999,
} as const;

export const type = {
  brand: {
    fontFamily: 'Fredoka_600SemiBold',
    fontSize: 28,
    letterSpacing: -0.5,
  },
  title: {
    fontFamily: 'Fredoka_500Medium',
    fontSize: 22,
    letterSpacing: -0.3,
  },
  body: {
    fontFamily: 'Fredoka_400Regular',
    fontSize: 16,
  },
  caption: {
    fontFamily: 'Fredoka_400Regular',
    fontSize: 13,
  },
  button: {
    fontFamily: 'Fredoka_500Medium',
    fontSize: 16,
  },
} as const;

export const motion = {
  press: { damping: 16, stiffness: 280 },
  spring: { damping: 18, stiffness: 220 },
  soft: { damping: 20, stiffness: 160 },
} as const;
