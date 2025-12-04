import { diff_match_patch } from 'diff-match-patch';

export interface DiffChunk {
    type: 'equal' | 'insert' | 'delete';
    text: string;
}

export const parseDiff = (diffs: [number, string][]): DiffChunk[] => {
    return diffs.map(([type, text]) => {
        let chunkType: 'equal' | 'insert' | 'delete' = 'equal';
        if (type === 1) chunkType = 'insert';
        if (type === -1) chunkType = 'delete';
        return { type: chunkType, text };
    });
};

export const calculateDiffStats = (diffs: [number, string][]) => {
    let additions = 0;
    let deletions = 0;

    diffs.forEach(([type, text]) => {
        if (type === 1) additions += text.length; // Count characters or lines? Let's stick to chars for now or maybe lines if we split
        if (type === -1) deletions += text.length;
    });

    return { additions, deletions };
};
