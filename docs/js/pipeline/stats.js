// Aggregate hit events into rallies and shot-type statistics.
// Mirrors backend/app/pipeline/stats.py.

/**
 * Assign each hit a rally index. A gap longer than `rallyGapSeconds`
 * between consecutive hits starts a new rally (the ball went out of
 * play / point ended).
 */
export function segmentRallies(hitTimes, rallyGapSeconds) {
  if (hitTimes.length === 0) return [];
  const rallyIndices = [0];
  for (let i = 1; i < hitTimes.length; i++) {
    const gap = hitTimes[i] - hitTimes[i - 1];
    rallyIndices.push(rallyIndices[rallyIndices.length - 1] + (gap > rallyGapSeconds ? 1 : 0));
  }
  return rallyIndices;
}

/**
 * Build shot-level stats from hit events.
 * `classifyFn(hit, isFirstHitOfRally)` is injected so this module stays
 * independent of pose data - it only knows about hit timing.
 */
export function buildStats(hits, classifyFn, rallyGapSeconds) {
  const rallyIndices = segmentRallies(
    hits.map((h) => h.t),
    rallyGapSeconds
  );
  const shots = [];
  const shotCounts = {};

  hits.forEach((hit, i) => {
    const rallyIndex = rallyIndices[i];
    const isFirst = i === 0 || rallyIndices[i - 1] !== rallyIndex;
    const shotType = classifyFn(hit, isFirst);
    shots.push({ t: hit.t, side: hit.side, shotType, rallyIndex });
    shotCounts[shotType] = (shotCounts[shotType] || 0) + 1;
  });

  const rallyCount = rallyIndices.length ? rallyIndices[rallyIndices.length - 1] + 1 : 0;
  return { shots, rallyCount, shotCounts };
}
