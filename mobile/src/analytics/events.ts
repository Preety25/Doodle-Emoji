/** Typed analytics placeholder — local console log only, no platform SDK. */

export type AnalyticsEvent =
  | 'app_open'
  | 'canvas_started'
  | 'doodle_completed'
  | 'transform_started'
  | 'transform_succeeded'
  | 'transform_failed'
  | 'style_selected'
  | 'try_another'
  | 'edit_doodle'
  | 'saved'
  | 'shared'
  | 'new_doodle';

export type AnalyticsProps = Record<string, string | number | boolean | null | undefined>;

const buffer: { event: AnalyticsEvent; props?: AnalyticsProps; at: string }[] = [];

export function track(event: AnalyticsEvent, props?: AnalyticsProps): void {
  const entry = { event, props, at: new Date().toISOString() };
  buffer.push(entry);
  // Local log OK — no Amplitude/Segment/etc.
  // eslint-disable-next-line no-console
  console.log('[analytics]', event, props ?? {});
}

export function getAnalyticsBuffer() {
  return [...buffer];
}
