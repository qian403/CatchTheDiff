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
