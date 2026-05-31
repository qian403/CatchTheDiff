export interface NewsVersion {
    id: number;
    news_id: number;
    time: number;
    title: string;
    body: string;
}

export interface News {
    id: number;
    url: string;
    normalized_id: string;
    source: number;
    created_at: number;
    last_fetch_at: number;
    last_changed_at: number;
    error_count: number;
    versions: NewsVersion[];
}

export interface NewsDiff {
    diff_title: [number, string][];
    diff_body: [number, string][];
}

export interface NewsSource {
    id: number;
    name: string;
    color: string;
}

export interface StatsOverview {
    totalNews: number;
    totalEdits: number;
    mostActiveSource: { name: string; editCount: number } | null;
    mostEditedNews: { title: string; versionCount: number } | null;
}

export interface EditFrequencyItem {
    sourceId: number;
    sourceName: string;
    newsCount: number;
    editCount: number;
    editRatio: number;
}

export interface TimelineSource {
    sourceName: string;
    data: Record<string, { newNews: number; edits: number }>;
}

export interface TimelineData {
    sources: TimelineSource[];
    dates: string[];
}
