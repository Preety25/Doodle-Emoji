import AsyncStorage from '@react-native-async-storage/async-storage';

import type { Creation } from '../models/types';

const LIBRARY_KEY = 'dooji.library.v1';

export async function loadLibrary(): Promise<Creation[]> {
  try {
    const raw = await AsyncStorage.getItem(LIBRARY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Creation[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export async function saveLibrary(creations: Creation[]): Promise<void> {
  await AsyncStorage.setItem(LIBRARY_KEY, JSON.stringify(creations));
}

export async function upsertCreation(creation: Creation): Promise<Creation[]> {
  const list = await loadLibrary();
  const idx = list.findIndex((c) => c.id === creation.id);
  const next = [...list];
  if (idx >= 0) next[idx] = creation;
  else next.unshift(creation);
  await saveLibrary(next);
  return next;
}

export async function removeCreation(id: string): Promise<Creation[]> {
  const list = await loadLibrary();
  const next = list.filter((c) => c.id !== id);
  await saveLibrary(next);
  return next;
}
