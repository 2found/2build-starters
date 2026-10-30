// Every query key comes from qk so invalidation can target a whole feature.
export const qk = {
  health: () => ['health'] as const,
}
