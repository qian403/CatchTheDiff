import type { NewsSource } from '../types';

export const NEWS_SOURCES: Record<number, NewsSource> = {
    1: { id: 1, name: "中央廣播電台", color: "#EF4444" },
    2: { id: 2, name: "中時新聞網", color: "#3B82F6" },
    3: { id: 3, name: "中央社", color: "#10B981" },
    4: { id: 4, name: "ETtoday新聞雲", color: "#F59E0B" },
    5: { id: 5, name: "自由時報", color: "#8B5CF6" },
    6: { id: 6, name: "新頭殼", color: "#EC4899" },
    7: { id: 7, name: "NOWnews今日新聞", color: "#06B6D4" },
    8: { id: 8, name: "聯合新聞網", color: "#F97316" },
    9: { id: 9, name: "TVBS新聞", color: "#6366F1" },
    10: { id: 10, name: "中廣新聞網", color: "#14B8A6" },
    11: { id: 11, name: "公視新聞網", color: "#84CC16" },
    12: { id: 12, name: "台視新聞", color: "#EAB308" },
    13: { id: 13, name: "華視新聞", color: "#0EA5E9" },
    14: { id: 14, name: "民視新聞", color: "#A855F7" },
    15: { id: 15, name: "三立新聞", color: "#22C55E" },
    16: { id: 16, name: "風傳媒", color: "#64748B" },
    17: { id: 17, name: "關鍵評論網", color: "#0F172A" },
    18: { id: 18, name: "報導者", color: "#000000" }
};

export const getSourceInfo = (id: number): NewsSource => {
    return NEWS_SOURCES[id] || { id, name: `未知來源 (${id})`, color: "#94A3B8" };
};
