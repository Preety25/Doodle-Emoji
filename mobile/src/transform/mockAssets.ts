/**
 * Bundled V4-era style sample PNGs for MOCK mode.
 * These are curated docs/refs art-direction assets (jelly gummy / clay / plush / glossy),
 * used where practical in place of live V4.x run outputs (gitignored).
 * Never contains prompts, xAI URLs, or API keys.
 */

import type { StyleId } from '../models/types';

// Metro requires static require() paths.
const PRIMARY: Record<StyleId, number> = {
  gummy: require('../../assets/mock/gummy.png'),
  clay: require('../../assets/mock/clay.png'),
  plush: require('../../assets/mock/plush.png'),
  glossy: require('../../assets/mock/glossy.png'),
};

const ALTS: Partial<Record<StyleId, number[]>> = {
  gummy: [
    require('../../assets/mock/gummy_alt.png'),
    require('../../assets/mock/gummy_alt2.png'),
  ],
};

export function mockAssetModule(style: StyleId, variation = 0): number {
  const alts = ALTS[style];
  if (alts && alts.length && variation > 0) {
    return alts[(variation - 1) % alts.length];
  }
  return PRIMARY[style];
}
