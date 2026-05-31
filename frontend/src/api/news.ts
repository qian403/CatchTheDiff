import apiClient from './client';
import type { News, NewsDiff } from '../types';
import type { SortBy } from '../types/filters';

interface NewsListParams {
    skip: number;
    limit: number;
    q?: string;
    date?: string;
    sort_by?: SortBy;
    sources?: number[];
}

export const fetchNewsList = async (
    skip: number = 0,
    limit: number = 30,
    query?: string,
    sources?: number[],
    date?: string,
    sortBy?: SortBy
): Promise<News[]> => {
    const params: NewsListParams = { skip, limit };
    if (query) params.q = query;
    if (date) params.date = date;
    if (sortBy) params.sort_by = sortBy;
    if (sources && sources.length > 0) params.sources = sources;

    const response = await apiClient.get<News[]>('/news', {
        params,
        paramsSerializer: {
            indexes: null // This ensures arrays are serialized as sources=1&sources=2 instead of sources[]=1
        }
    });
    return response.data;
};

export const fetchChangedNews = async (skip: number = 0, limit: number = 30): Promise<News[]> => {
    const response = await apiClient.get<News[]>('/news/changes', {
        params: { skip, limit }
    });
    return response.data;
};

export const fetchNewsDetail = async (id: number): Promise<News> => {
    const response = await apiClient.get<News>(`/news/${id}`);
    return response.data;
};

export const fetchNewsDiff = async (newsId: number, v1: number, v2: number): Promise<NewsDiff> => {
    const response = await apiClient.get<NewsDiff>(`/news/${newsId}/diff`, {
        params: { v1, v2 }
    });
    return response.data;
};
