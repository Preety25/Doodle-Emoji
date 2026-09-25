/**
 * Provider-agnostic Usage / Entitlement placeholder.
 * No pricing UI, no hard-coded free-limit numbers.
 */

export type EntitlementKind = 'transform' | 'save' | 'share';

export interface UsageSnapshot {
  transformsUsed: number;
  lastTransformAt?: string;
}

export interface EntitlementCheck {
  allowed: boolean;
  reason?: 'ok' | 'unavailable' | 'deferred';
}

export interface UsageEntitlement {
  snapshot(): UsageSnapshot;
  can(kind: EntitlementKind): EntitlementCheck;
  record(kind: EntitlementKind): void;
}

class AlwaysAllowUsage implements UsageEntitlement {
  private transformsUsed = 0;
  private lastTransformAt?: string;

  snapshot(): UsageSnapshot {
    return {
      transformsUsed: this.transformsUsed,
      lastTransformAt: this.lastTransformAt,
    };
  }

  can(_kind: EntitlementKind): EntitlementCheck {
    return { allowed: true, reason: 'ok' };
  }

  record(kind: EntitlementKind): void {
    if (kind === 'transform') {
      this.transformsUsed += 1;
      this.lastTransformAt = new Date().toISOString();
    }
  }
}

export const usage: UsageEntitlement = new AlwaysAllowUsage();
