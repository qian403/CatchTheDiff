import DOMPurify from 'dompurify';
import { diff_match_patch, DIFF_EQUAL, DIFF_DELETE, DIFF_INSERT } from 'diff-match-patch';

export interface DiffChunk {
  type: 'equal' | 'insert' | 'delete';
  text: string;
}

export const parseDiff = (diffs: [number, string][]): DiffChunk[] => {
  return diffs.map(([type, text]) => {
    let chunkType: DiffChunk['type'] = 'equal';
    if (type === 1) chunkType = 'insert';
    if (type === -1) chunkType = 'delete';
    return { type: chunkType, text };
  });
};

export const calculateDiffStats = (diffs: [number, string][]): { additions: number; deletions: number } => {
  let additions = 0;
  let deletions = 0;

  diffs.forEach(([type, text]) => {
    if (type === 1) additions += text.length;
    if (type === -1) deletions += text.length;
  });

  return { additions, deletions };
};

/**
 * Escape a raw string so it is safe to inject between HTML tags.
 * Must run BEFORE wrapping any segment in <del>/<ins>, otherwise an attacker
 * controlled title could inject markup that survives sanitization context.
 */
const escapeHtml = (s: string): string =>
  s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

const SANITIZE_OPTS = {
  ALLOWED_TAGS: ['del', 'ins'],
  ALLOWED_ATTR: ['class'],
};

/**
 * Character-level diff highlight for title comparison.
 * Uses diff-match-patch (semantic cleanup) so adjacent runs collapse into
 * human-readable chunks instead of jagged single-character marks.
 *
 * Returns sanitized HTML safe for `v-html`. Caller is responsible for the
 * `v-html` decision; we still sanitize defensively in case the allowed-tag
 * policy ever drifts.
 */
export const highlightTitleDiff = (
  oldText: string,
  newText: string,
  mode: 'old' | 'new',
): string => {
  if (!oldText && !newText) return '';

  const dmp = new diff_match_patch();
  const diffs = dmp.diff_main(oldText, newText);
  dmp.diff_cleanupSemantic(diffs);

  let result = '';
  for (const [op, text] of diffs) {
    const safe = escapeHtml(text);
    if (op === DIFF_EQUAL) {
      result += safe;
    } else if (op === DIFF_DELETE && mode === 'old') {
      result += `<del class="diff-del">${safe}</del>`;
    } else if (op === DIFF_INSERT && mode === 'new') {
      result += `<ins class="diff-ins">${safe}</ins>`;
    }
  }

  return DOMPurify.sanitize(result, SANITIZE_OPTS);
};
