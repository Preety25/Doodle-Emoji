import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { StyleSheet, View } from 'react-native';

import { GeneratingView } from '../components/Feedback';
import { colors } from '../design/tokens';
import { useApp } from '../state/AppContext';

export default function GeneratingScreen() {
  const app = useApp();
  const router = useRouter();

  useEffect(() => {
    if (app.phase === 'result') router.replace('/result');
    if (app.phase === 'canvas') router.replace('/');
  }, [app.phase, router]);

  return (
    <View style={styles.root}>
      <GeneratingView copy={app.generatingCopy} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.surface },
});
